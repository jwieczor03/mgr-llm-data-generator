import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from application_api.ddl_worker import main


def analyze(request, emit):
    import pglast

    parsed = pglast.parse_sql(request["sql"])
    emit({"type": "checkpoint", "statements": len(parsed)})
    return {
        "type": "result",
        "version": pglast.__version__,
        "node": type(parsed[0].stmt).__name__,
    }


raise SystemExit(main(analyze))
