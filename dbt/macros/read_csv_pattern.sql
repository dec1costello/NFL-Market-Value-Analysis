{% macro read_csv_pattern(path_pattern) %}
    {% set query -%}
        SELECT * FROM read_csv_auto(
            '{{ path_pattern }}',
            header=true,
            filename=true,
            hive_partitioning=true
        )
    {%- endset %}
    {{ return(query) }}
{% endmacro %}