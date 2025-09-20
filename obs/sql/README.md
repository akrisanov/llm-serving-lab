# ClickHouse SQL Scripts

This directory contains SQL scripts and templates for ClickHouse database initialization and schema management.

## Files

### `001-users-and-db.sql.j2`

Jinja2 template for initial database and user setup. This template is processed by Ansible during deployment to create:

- Database (`{{ ch_db }}`)
- User with sha256 password authentication (`{{ ch_user }}`)
- Basic permissions (CREATE, INSERT, SELECT)

## File Naming Convention

- **`.sql.j2`** - Jinja2 templates for Ansible deployment (parameterized)
- **Sequential numbering** - `001-`, `002-`, etc. for execution order
- **Descriptive names** - explain the purpose of each script

## Usage

### Deployment via Ansible

SQL templates are automatically processed and deployed when running the observability stack playbook:

```bash
cd ../ansible
ansible-playbook -i inventory.ini playbooks/site.yml
```

### Manual ClickHouse Operations

To connect to ClickHouse manually for schema changes or debugging:

```bash
# From your local machine (if ports are open)
clickhouse-client --host <obs-vm-ip> --port 9000 --user otel --password <CH_PASSWORD>

# From the obs VM
ssh ubuntu@<obs-vm-ip>
sudo docker exec -it obs-clickhouse-1 clickhouse-client --user otel --password <CH_PASSWORD>
```

### Schema Evolution

When adding new SQL scripts:

1. Create new `.sql.j2` template files with sequential naming (002-*, 003-*, etc.)
2. Update Ansible tasks to process additional templates if needed
3. Test changes in development environment first
4. Document schema changes in this README

## Best Practices

- **Use Jinja2 templates (.sql.j2)** for all SQL files requiring variable substitution
- **Sequential numbering** for migration-like scripts (001-, 002-, etc.)
- **Descriptive names** that explain the purpose of each script
- **Test in development** before deploying to production
- **Document schema changes** in this README as they evolve

## ClickHouse Schema Notes

Add notes about your specific schema design, table structures, and data models here as they evolve.

### Example Tables (to be documented)

- Metrics tables for OTLP data
- System monitoring tables
- Performance benchmark results
