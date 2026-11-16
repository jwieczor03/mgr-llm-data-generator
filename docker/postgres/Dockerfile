FROM postgres:18.7-bookworm
COPY docker/postgres/10-app-role.sh /docker-entrypoint-initdb.d/10-app-role.sh
RUN chmod 0755 /docker-entrypoint-initdb.d/10-app-role.sh
