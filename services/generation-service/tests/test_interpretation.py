import asyncio
import json
from dataclasses import replace

import pytest
from generation_service.bootstrap import create_interpretation_service
from generation_service.interpretation import (
    ApprovedRule,
    Column,
    Context,
    InterpretationError,
    PlanRequest,
    Profile,
    RelationRequest,
    RuleRequest,
    RuleType,
    Table,
)
from generation_service.llm import (
    Call,
    Identity,
    LlmClient,
    Response,
    TechnicalError,
    Usage,
    disclosure_hash,
)


class Fake:
    backend = 'fake'
    trusted_local = False
    recipient = 'recipient'
    supported_options = frozenset()

    def __init__(self, output):
        self.output = output
        self.calls = []

    async def send(self, call):
        self.calls.append(call)
        if self.output == 'failure':
            raise TechnicalError(Usage(input_tokens=3))
        return Response(self.output, Usage(input_tokens=7))


def context():
    return Context(project_id='p', preparation_operation_id='op', schema_version_id='v', ddl_hash='manifest',
                   ddl='CREATE TABLE orders (id int);',
                   tables=(Table(id='orders', name='orders', columns=(Column(id='oid', name='id'),
                           Column(id='customer', name='customer_id'), Column(id='region', name='region_id'))),
                           Table(id='clients', name='clients', columns=(Column(id='cid', name='id'), Column(id='cregion', name='region_id'))),
                           Table(id='products', name='products', columns=()),
                           Table(id='items', name='items', columns=())),
                   approved_rules=(ApprovedRule(id='r', definition={'value': 1}),))


def setup(output):
    fake = Fake(output)
    profile = Profile('model', (), 10000, 100, lambda messages: len(str(messages)))
    service = create_interpretation_service(lambda: LlmClient(fake), profile)
    return service, fake, profile


def execute(service, fake, profile, prepared, digest=None):
    async def go():
        deadline = asyncio.get_running_loop().time() + 5
        call = Call(prepared.preparation_operation_id, prepared.snapshot_hash, Identity('interpretation', '1'),
                    prepared.prompt, profile.model, prepared.messages, dict(profile.options),
                    profile.count_tokens(prepared.messages), profile.max_context_tokens, profile.output_tokens, deadline)
        approval = disclosure_hash(call, fake.recipient) if digest is None else digest
        return await getattr(service, 'interpret_' + prepared.operation)(prepared, deadline=deadline,
                                                                         disclosure_digest=approval)
    return asyncio.run(go())


def test_relations_and_scope():
    output = {'relations': [{'source_table_id': 'orders', 'target_table_id': 'clients',
              'column_pairs': [{'source_column_id': 'customer', 'target_column_id': 'cid'},
                               {'source_column_id': 'region', 'target_column_id': 'cregion'}], 'explanation': 'link'}]}
    service, fake, profile = setup(json.dumps(output))
    prepared = service.prepare_relations(RelationRequest(context=context()))
    result = execute(service, fake, profile, prepared)
    assert [pair.target_column_id for pair in result.value.relations[0].column_pairs] == ['cid', 'cregion']
    assert result.measurement.attempt.call_id and result.measurement.project_id == 'p'
    assert result.measurement.ddl_hash == 'manifest' and len(fake.calls) == 1
    assert 'CREATE TABLE orders' in fake.calls[0].messages[1].content
    fake.output = '{"relations":[]}'
    assert execute(service, fake, profile, prepared).value.relations == ()


def test_rule_question_proposal_and_missing_parameter():
    service, fake, profile = setup('{"kind":"question","question":"What?"}')
    request = RuleRequest(context=context(), rule_revision_id='rev', rule_text='age',
                          rule_catalog=(RuleType(type='minimum', description='min', required_parameters=('value',)),))
    prepared = service.prepare_rule(request)
    assert execute(service, fake, profile, prepared).value.kind == 'question'
    fake.output = '{"kind":"proposal","type":"minimum","parameters":{"value":18},"meaning":"adult"}'
    assert execute(service, fake, profile, prepared).measurement.revision_id == 'rev'
    fake.output = '{"kind":"proposal","type":"minimum","parameters":{},"meaning":"adult"}'
    with pytest.raises(InterpretationError, match='invalid_model_response'):
        execute(service, fake, profile, prepared)


def test_plan_clarifications_and_conflicts():
    service, fake, profile = setup('{"kind":"question","question":"What is VIP?"}')
    req = PlanRequest(context=context(), order_revision_id='rev', command='200 VIP orders')
    first = service.prepare_plan(req)
    assert execute(service, fake, profile, first).value.kind == 'question'
    prepared = service.prepare_plan(req.model_copy(update={'clarifications': ('VIP means active',)}))
    assert prepared.snapshot_hash != first.snapshot_hash and 'VIP means active' in prepared.context_json
    fake.output = json.dumps({'kind': 'plan', 'tables': [{'table_id': t, 'count': n} for t, n in
                             [('orders', 200), ('clients', 30), ('products', 10), ('items', 0)]]})
    assert len(execute(service, fake, profile, prepared).value.tables) == 4
    fake.output = '{"kind":"conflict","source":"ddl","reason":"forbidden","object_id":null}'
    assert execute(service, fake, profile, prepared).value.kind == 'conflict'
    fake.output = '{"kind":"conflict","source":"approved_rule","reason":"forbidden","object_id":"r"}'
    assert execute(service, fake, profile, prepared).value.kind == 'conflict'


@pytest.mark.parametrize('output', [
    '{"kind":"plan","tables":[{"table_id":"orders","count":true}]}',
    '{"kind":"plan","tables":[{"table_id":"orders","count":1.0}]}',
    '{"kind":"plan","tables":[{"table_id":"orders","count":"1"}]}',
    '{"kind":"plan","tables":[{"table_id":"orders","count":-1}]}',
    '{"kind":"plan","tables":[{"table_id":"orders"}]}',
    '{"kind":"plan","tables":[{"table_id":"foreign","count":1}]}',
    '{"kind":"plan","tables":[{"table_id":"orders","count":1},{"table_id":"orders","count":2}]}',
    '{"kind":"question","question":"x","tables":[]}',
    '{"kind":"conflict","source":"approved_rule","reason":"x","object_id":"foreign"}',
    'private raw output',
])
def test_invalid_output_keeps_measurement(output):
    service, fake, profile = setup(output)
    prepared = service.prepare_plan(PlanRequest(context=context(), order_revision_id='rev', command='orders'))
    with pytest.raises(InterpretationError) as exc:
        execute(service, fake, profile, prepared)
    assert exc.value.code == 'invalid_model_response' and exc.value.measurement.attempt.usage.input_tokens == 7
    assert output not in str(exc.value)


def test_approval_preflight_and_failure_measurement():
    service, fake, profile = setup('failure')
    prepared = service.prepare_relations(RelationRequest(context=context()))
    with pytest.raises(InterpretationError) as exc:
        execute(service, fake, profile, prepared, 'stale')
    assert exc.value.measurement is None and not fake.calls
    with pytest.raises(InterpretationError) as exc:
        execute(service, fake, profile, prepared)
    assert exc.value.code == 'technical_error' and exc.value.measurement.attempt.usage.input_tokens == 3
    assert len(fake.calls) == 1
    changed = replace(prepared, messages=prepared.messages + prepared.messages)
    with pytest.raises(InterpretationError):
        execute(service, fake, profile, changed)
    assert len(fake.calls) == 1


@pytest.mark.parametrize('output', [
    '{"kind":"plan","kind":"conflict","source":"ddl","reason":"x"}',
    '{"kind":"plan","tables":[{"table_id":"orders","count":1,"count":2}]}',
    '{"kind":"plan","tables":[{"table_id":"orders","count":NaN}]}',
    '{"kind":"plan","tables":[{"table_id":"orders","count":Infinity}]}',
])
def test_rejects_ambiguous_json(output):
    service, fake, profile = setup(output)
    prepared = service.prepare_plan(PlanRequest(context=context(), order_revision_id='rev', command='orders'))
    with pytest.raises(InterpretationError, match='invalid_model_response'):
        execute(service, fake, profile, prepared)


def test_changed_model_recipient_and_context_reject_old_consent():
    service, fake, profile = setup('{"relations":[]}')
    request = RelationRequest(context=context())
    original = service.prepare_relations(request)
    async def old_approval():
        call = Call('op', original.snapshot_hash, Identity('interpretation', '1'), original.prompt,
                    profile.model, original.messages, {}, profile.count_tokens(original.messages),
                    profile.max_context_tokens, profile.output_tokens, asyncio.get_running_loop().time() + 5)
        return disclosure_hash(call, fake.recipient)
    digest = asyncio.run(old_approval())
    changed_model = create_interpretation_service(lambda: LlmClient(fake), replace(profile, model='other'))
    new_prepared = changed_model.prepare_relations(request)
    with pytest.raises(InterpretationError):
        execute(changed_model, fake, replace(profile, model='other'), new_prepared, digest)
    with pytest.raises(InterpretationError):
        execute(changed_model, fake, replace(profile, model='other'), original, digest)
    changed_request = request.model_copy(update={'context': context().model_copy(update={'ddl': 'different'})})
    with pytest.raises(InterpretationError):
        execute(service, fake, profile, service.prepare_relations(changed_request), digest)
    fake.recipient = 'other recipient'
    with pytest.raises(InterpretationError):
        execute(service, fake, profile, original, digest)
    assert not fake.calls


def test_relation_columns_are_owned_and_not_repeated():
    service, fake, profile = setup('')
    prepared = service.prepare_relations(RelationRequest(context=context()))
    for pairs in ([{'source_column_id': 'cid', 'target_column_id': 'cid'}],
                  [{'source_column_id': 'customer', 'target_column_id': 'cid'},
                   {'source_column_id': 'customer', 'target_column_id': 'cid'}], []):
        fake.output = json.dumps({'relations': [{'source_table_id': 'orders', 'target_table_id': 'clients',
                                                 'column_pairs': pairs, 'explanation': 'x'}]})
        with pytest.raises(InterpretationError, match='invalid_model_response'):
            execute(service, fake, profile, prepared)


def test_missing_profile_client_budget_and_expired_deadline():
    service, fake, profile = setup('{"relations":[]}')
    request = RelationRequest(context=context())
    with pytest.raises(InterpretationError, match='technical_error'):
        create_interpretation_service(None, None).prepare_relations(request)
    prepared = service.prepare_relations(request)
    with pytest.raises(InterpretationError) as exc:
        execute(create_interpretation_service(None, profile), fake, profile, prepared)
    assert exc.value.measurement is None
    limited = replace(profile, max_context_tokens=1)
    too_large = create_interpretation_service(lambda: LlmClient(fake), limited)
    with pytest.raises(InterpretationError) as exc:
        execute(too_large, fake, limited, too_large.prepare_relations(request))
    assert exc.value.measurement is None and not fake.calls
    async def expired():
        with pytest.raises(InterpretationError) as error:
            await service.interpret_relations(prepared, deadline=0, disclosure_digest='invalid')
        assert error.value.measurement is None
    asyncio.run(expired())


def test_invalid_or_reused_client_has_no_old_measurement():
    service, fake, profile = setup('{"relations":[]}')
    prepared = service.prepare_relations(RelationRequest(context=context()))
    reused = LlmClient(fake)
    reused.attempts.append(execute(service, fake, profile, prepared).measurement.attempt)
    for factory in (lambda: object(), lambda: reused):
        invalid = create_interpretation_service(factory, profile)
        with pytest.raises(InterpretationError) as exc:
            execute(invalid, fake, profile, prepared)
        assert exc.value.code == 'technical_error' and exc.value.measurement is None



def test_deep_json_and_overflow_are_safe_invalid_response():
    service, fake, profile = setup('')
    request = RuleRequest(context=context(), rule_revision_id='r', rule_text='rule',
                          rule_catalog=(RuleType(type='x', description='x'),))
    prepared = service.prepare_rule(request)
    for parameter in ('1e500', '[' * 2000 + '0' + ']' * 2000):
        fake.output = '{"kind":"proposal","type":"x","parameters":{"value":' + parameter + '},"meaning":"m"}'
        with pytest.raises(InterpretationError) as exc:
            execute(service, fake, profile, prepared)
        assert exc.value.code == 'invalid_model_response' and exc.value.measurement is not None
        assert parameter not in str(exc.value)
