![Status](https://img.shields.io/badge/status-active-success.svg)
![Domain](https://img.shields.io/badge/domain-Sports%20Analytics%20%7C%20ML-blue.svg)
![Warehouse](https://img.shields.io/badge/warehouse-DuckDB-orange.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![dbt](https://img.shields.io/badge/dbt-1.5+-orange.svg)
![DuckDB](https://img.shields.io/badge/DuckDB-0.9+-yellow.svg)
![ML](https://img.shields.io/badge/PyTorch%20%7C%20PyMC%20%7C%20Optuna-purple.svg)
<br />
[GitHub](https://github.com/dec1costello) | [Kaggle](https://www.kaggle.com/dec1costello) | [LinkedIn](https://www.linkedin.com/in/declan-costello-7423aa137/)
<br />
Author: Declan Costello

<a name="readme-top"></a>

<p align="center">
<img height="263" width="186" src="https://github.com/user-attachments/assets/574ae0e8-38a0-44dc-b72c-ec4217bb03b2"/>  

</p>

<h1 align="center">NFL Player Contract Value Prediction</h1>

**Business Objective:** Predict NFL player contract terms (years, average annual value, guarantees, percent of team cap space) to identify market inefficiencies and optimize team salary cap management.

**Technical Approach:** A three stage ML pipeline using modern analytics engineering patterns. Features are engineered with SQL (dbt) and enriched with player archetypes via clustering. Contract length is predicted with PyTorch, and financial terms are estimated with PyMC Bayesian regression.

**Key Results:**
- ✅ **Position Specific Archetypes:** K-Means clustering within each position (QB, WR, RB, etc) to discover player subtypes
- ✅ **Probabilistic Financial Modeling:** Bayesian regression with credible intervals for risk aware decision making
- ✅ **Reproducible ML Pipeline:** Deterministic feature engineering and model training
- ✅ **Operational Analytics:** Predictions stored as DuckDB tables for team analytics consumption
- ✅ **Kubernetes Orchestration:** Scalable, position specific model deployment

**Architecture Rationale:** DuckDB was selected as the central warehouse for its embedded nature and SQL compliance, eliminating cloud costs while handling NFL datasets efficiently. The three stage pipeline (archetypes → years → financials) mirrors real world contract logic while maintaining statistical rigor.

## 🏗️ Architecture Diagram

This NFL contract prediction system employs a sequential pipeline that mirrors front office decision making. Player performance data flows through position specific feature engineering, is enriched with discovered archetypes ("Scrambler QB" or "Fullback RB"), predicts contract length via neural networks, and finally estimates financial terms with Bayesian uncertainty. All predictions are stored as queryable tables, enabling immediate market value insights.
```mermaid


graph TB
    %% === PROFESSIONAL RED WHITE BLUE THEME ===
    classDef infrastructure fill:#eef2ff,stroke:#1e3a8a,stroke-width:2.5px,color:#1e3a8a
    classDef storage fill:#f9fafb,stroke:#374151,stroke-width:2.5px,color:#111827
    classDef stage1 fill:#eff6ff,stroke:#3b82f6,stroke-width:2.5px,color:#1e3a8a
    classDef stage2 fill:#f8fafc,stroke:#3b82f6,stroke-width:2.5px,color:#1e3a8a
    classDef stage3 fill:#fef2f2,stroke:#dc2626,stroke-width:2.5px,color:#991b1b
    classDef features fill:#f1f5f9,stroke:#334155,stroke-width:2.5px,color:#0f172a
    classDef model fill:#ffffff,stroke:#3b82f6,stroke-width:2.5px,color:#1e3a8a
    classDef output fill:#fff7ed,stroke:#dc2626,stroke-width:2.5px,color:#991b1b

    classDef bold font-weight:bold

    %% === INFRASTRUCTURE ===
    subgraph INFRA ["<b>Infrastructure</b>"]
        DUCKDB["<b>🦆 DuckDB Warehouse</b><br/><i>nfl_contracts.duckdb</i>"]
        K8S["<b>⚓ Kubernetes</b><br/><i>Orchestrates Position Jobs</i>"]
        DBT["<b>🛠️ dbt</b><br/><i>SQL Transformations</i>"]
    end

    %% === PIPELINE ===
    subgraph DATA_FLOW ["Prediction Pipeline</b>"]
        subgraph STAGE_1 ["<b>Position Based</b>"]
            CLUSTERING["<b>K-Means + Elbow Method</b><br/>Archetype Labels"]
            adjusted_metric["<b>Adjusted Metric</b><br/>Performance Calculation"]
        end

        subgraph STAGE_2 ["<b>Duration Terms</b>"]
            YEAR_MODELS["<b>Age Curve</b><br/>Snap Share Projections"]
            YEAR_PREDS["<b>Year Classification</b><br/>2-5 Years Prediction"]
        end

        subgraph STAGE_3 ["<b>Financial Terms</b>"]
            FINANCIAL_MODELS["<b>% of Salary Cap</b><br/>Per Contract Years<br/>💰"]
        end
    end

    %% === STORAGE ===
    subgraph STORAGE ["<b>Storage Layer</b>"]
        FEATURES["<b>Feature Store</b><br/>Position Statistics"]
        RESULTS["<b>Predictions</b><br/>🏈 "]
    end

    %% === CONNECTIONS ===
     DUCKDB -->|"<i>Serves</i>"| FEATURES
    DBT -->|"<i>Transforms</i>"| FEATURES
    K8S -->|"<i>Orchestrates</i>"| DATA_FLOW
    K8S -->|"<i>Deploys</i>"| DATA_FLOW

    FEATURES --> STAGE_1
    STAGE_1 --> STAGE_2
    FEATURES --> STAGE_2

    YEAR_MODELS --> YEAR_PREDS
    YEAR_PREDS --> STAGE_3
    STAGE_1 --> STAGE_3
    FEATURES --> STAGE_3
    FINANCIAL_MODELS --> RESULTS

    %% === APPLY STYLES ===
    class INFRA,DUCKDB,K8S,DBT infrastructure
    class STORAGE,FEATURES,RESULTS storage
    class STAGE_1 stage1
    class STAGE_2 stage2
    class STAGE_3 stage3
    class FEATURES features
    class CLUSTERING,YEAR_MODELS,FINANCIAL_MODELS model
    class adjusted_metric,YEAR_PREDS,RESULTS output
    class STAGE_1,STAGE_2,STAGE_3 bold

    %% === LINK COLORS MATCH SOURCE NODES ===
    linkStyle 0 stroke:#1e3a8a,stroke-width:3px
    linkStyle 1 stroke:#1e3a8a,stroke-width:3px
    linkStyle 2 stroke:#1e3a8a,stroke-width:3px
    linkStyle 3 stroke:#1e3a8a,stroke-width:3px

    linkStyle 4 stroke:#334155,stroke-width:3px
    linkStyle 5 stroke:#3b82f6,stroke-width:3px
    linkStyle 6 stroke:#334155,stroke-width:3px

    linkStyle 7 stroke:#3b82f6,stroke-width:3px
    linkStyle 8 stroke:#3b82f6,stroke-width:3px
    linkStyle 9 stroke:#3b82f6,stroke-width:3px
    linkStyle 10 stroke:#334155,stroke-width:3px
    linkStyle 11 stroke:#dc2626,stroke-width:3px



```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🌵 Repository Structure
    
    nfl-contracts/
    ├── 📁 data/
    │   ├── 📁 raw/                   
    │   │   ├── contracts.csv
    │   │   ├── stats.csv
    │   │   └── physical.csv
    │   └── 📁 processed/             # Intermediate processed data
    │       └── README.md
    │
    ├── 📁 warehouse/                 # DuckDB warehouse directory
    │   ├── nfl_contracts.duckdb       # MAIN DATABASE FILE
    │   └── backups/                   # Daily backups
    │
    ├── 📁 dbt/                       # SQL transformations
    │   ├── dbt_project.yml            # dbt configuration
    │   ├── 📁 models/
    │   │   ├── 📁 bronze/            # Raw table staging
    │   │   │   ├── contracts.sql
    │   │   │   ├── stats.sql
    │   │   │   └── physical.sql
    │   │   ├── 📁 silver/            # Cleaned business tables
    │   │   │   ├── dim_players.sql
    │   │   │   ├── fact_performance.sql
    │   │   │   └── fact_contracts.sql
    │   │   └── 📁 gold/              # Feature engineering
    │   │       ├── features/
    │   │       │   ├── qb_features.sql
    │   │       │   ├── wr_features.sql
    │   │       │   └── position_features.sql
    │   │       ├── qbr_ratings.sql
    │   │       └── z_scores.sql
    │   ├── 📁 tests/                  # Data quality tests
    │   │   ├── contracts_test.sql
    │   │   └── uniqueness_test.sql
    │   └── 📁 macros/                 # Reusable SQL
    │       └── calculate_qbr.sql
    │
    ├── 📁 src/                       # Python source code
    │   ├── 📁 clustering/            # Stage 1: Archetype discovery
    │   │   ├── __init__.py
    │   │   ├── qb_clustering.py
    │   │   ├── wr_clustering.py
    │   │   ├── utils.py
    │   │   └── elbow_visualization.py
    │   │
    │   ├── 📁 years_model/           # Stage 2: Contract length
    │   │   ├── __init__.py
    │   │   ├── train_qb_years.py
    │   │   ├── train_wr_years.py
    │   │   ├── predict.py
    │   │   └── model_architectures.py
    │   │
    │   ├── 📁 financial_model/       # Stage 3: Financial terms
    │   │   ├── __init__.py
    │   │   ├── qb_bayesian.py
    │   │   ├── wr_bayesian.py
    │   │   ├── posterior_analysis.py
    │   │   └── uncertainty_plots.py
    │   │
    │   ├── 📁 utils/                 # Shared utilities
    │   │   ├── duckdb_connector.py
    │   │   ├── feature_loader.py
    │   │   ├── logger_config.py
    │   │   └── config.py
    │   │
    │   └── 📁 api/                   # FastAPI for serving
    │       ├── main.py
    │       ├── schemas.py
    │       └── routers/
    │           ├── qb_router.py
    │           └── wr_router.py
    │
    ├── 📁 models/                    # Trained model artifacts
    │   ├── 📁 pytorch/
    │   │   ├── qb_years_model.pt
    │   │   ├── wr_years_model.pt
    │   │   └── model_metadata.json
    │   └── 📁 pymc/
    │       ├── qb_financial.nc       # NetCDF with posterior samples
    │       └── wr_financial.nc
    │
    ├── 📁 docker/                    # Container configurations
    │   ├── Dockerfile.clustering
    │   ├── Dockerfile.pytorch
    │   ├── Dockerfile.pymc
    │   ├── Dockerfile.api
    │   └── docker-compose.yml
    │
    ├── 📁 k8s/                       # Kubernetes manifests
    │   ├── 📁 manifests/
    │   │   ├── 00-namespace.yaml
    │   │   ├── 01-configmap.yaml
    │   │   ├── 02-secrets.yaml
    │   │   ├── 03-persistent-volume.yaml
    │   │   ├── 04-clustering-job.yaml
    │   │   ├── 05-pytorch-deployment.yaml
    │   │   ├── 06-pymc-deployment.yaml
    │   │   ├── 07-services.yaml
    │   │   └── 08-ingress.yaml
    │   └── 📁 configs/
    │       ├── prometheus-values.yaml
    │       └── grafana-dashboard.yaml
    │
    ├── 📁 tests/                     # Test suite
    │   ├── 📁 unit/
    │   │   ├── test_clustering.py
    │   │   └── test_features.py
    │   ├── 📁 integration/
    │   │   ├── test_pipeline.py
    │   │   └── test_duckdb.py
    │   └── 📁 e2e/
    │       └── test_full_pipeline.py
    │
    ├── 📁 scripts/                   # Utility scripts
    │   ├── init_duckdb.py
    │   ├── run_full_pipeline.sh
    │   ├── backup_warehouse.sh
    │   └── deploy_to_k8s.sh
    │
    ├── 📁 docs/                      # Documentation
    │   ├── architecture.md
    │   ├── api_documentation.md
    │   ├── data_dictionary.md
    │   └── setup_guide.md
    │
    ├── 📁 .github/                   # CI/CD workflows
    │   └── 📁 workflows/
    │       ├── test.yml
    │       ├── build.yml
    │       └── deploy.yml
    │
    ├── 📁 .vscode/                   # VS Code settings
    │   ├── settings.json
    │   └── extensions.json
    │
    ├── pyproject.toml               # UV/Python dependencies
    ├── uv.lock                      # UV lock file
    ├── .env.example                 # Environment template
    ├── .gitignore
    ├── .dockerignore
    ├── README.md                    
    └── Makefile                     # Common commands

<p align="right">(<a href="#readme-top">back to top</a>)</p>    
