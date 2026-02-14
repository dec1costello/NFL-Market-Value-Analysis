{% macro clean_dollar_amount(column_name) %}
    TRY_CAST(REPLACE(REPLACE({{ column_name }}, '$', ''), ',', '') AS DECIMAL(18,2))
{% endmacro %}