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

<p align="center">
<img height="263" width="186" src="https://github.com/user-attachments/assets/574ae0e8-38a0-44dc-b72c-ec4217bb03b2"/>  

</p>

<h1 align="center">NFL Player Contract Value Prediction</h1>

**Business Objective:** Predict NFL player contract terms (years, average annual value, guarantees) to identify market inefficiencies and optimize team salary cap management.

**Technical Approach:** A three-stage ML pipeline using modern analytics engineering patterns. Features are engineered with SQL (dbt) and enriched with player archetypes via clustering. Contract length is predicted with PyTorch neural networks, and financial terms are estimated with PyMC Bayesian regression—providing both point estimates and uncertainty quantification.

**Key Results:**
- ✅ **Position-Specific Archetypes:** K-Means clustering within each position (QB, WR, DL, etc.) to discover player subtypes
- ✅ **Probabilistic Financial Modeling:** Bayesian regression with credible intervals for risk-aware decision making
- ✅ **Reproducible ML Pipeline:** Deterministic feature engineering and model training
- ✅ **Operational Analytics:** Predictions stored as DuckDB tables for team analytics consumption
- ✅ **Kubernetes Orchestration:** Scalable, position-specific model deployment

**Architecture Choice Rationale:** DuckDB was selected as the central warehouse for its embedded nature and SQL compliance, eliminating cloud costs while handling NFL datasets efficiently. The three-stage pipeline (archetypes → years → financials) mirrors real-world contract negotiation logic while maintaining statistical rigor.

## 🏗️ Architecture Diagram

This NFL contract prediction system employs a sequential pipeline that mirrors actual team decision-making. Player performance data flows through position-specific feature engineering, is enriched with discovered archetypes (e.g., "Scrambler QB" or "Deep Threat WR"), predicts contract length via neural networks, and finally estimates financial terms with Bayesian uncertainty. All predictions are stored as queryable tables, enabling team analysts to immediately access market value insights while front offices maintain full auditability of the modeling process.

```mermaid
graph TB
 %% === STYLING ===
    classDef stage1 fill:#f0fff4,stroke:#48bb78,stroke-width:3px,color: #2a4365
    classDef stage2 fill:#fef3c7,stroke:#d69e2e,stroke-width:3px,color:#744210
    classDef stage3 fill:#ebf8ff,stroke:#4299e1,stroke-width:3px,color:#22543d
    classDef features fill:#fef3c7,stroke:#eab308,stroke-width:2px,color:#854d0e
    classDef model fill:#e0f7fa,stroke:#00bcd4,stroke-width:2px,color:#006064
    classDef output fill:#e3f2fd,stroke:#2196f3,stroke-width:2px,color:#0d47a1
    classDef infra fill:#f5f3ff,stroke:#8b5cf6,stroke-width:2px,color:#5b21b6
    classDef storage fill:#fff0f0,stroke:#FF6B6B,stroke-width:2px,stroke-dasharray:5 5,color:#c53030

    %% === INFRASTRUCTURE LAYERS ===
    subgraph INFRA ["🛠️ Infrastructure"]
        DUCKDB["🦆 DuckDB Warehouse<br/>nfl_contracts.duckdb"]
        K8S["⚓ Kubernetes<br/>Orchestrates Position Jobs"]
        DBT["⚙️ dbt<br/>SQL Transformations"]
    end

    %% === DATA FLOW ===
    subgraph DATA_FLOW ["📊 Data Pipeline"]
        %% === STAGE 1: ARCHETYPE DISCOVERY ===
        subgraph STAGE_1 ["Position Archetypes"]
            CLUSTERING["Position Clustering<br/>K-Means + Elbow Method"]
            ARCHETYPES["Archetype Labels"]
        end

        %% === STAGE 2: YEAR PREDICTION ===
        subgraph STAGE_2 ["Contract Length"]
            YEAR_MODELS["Position Year Models<br/>PyTorch NN"]
            YEAR_PREDS["Year Predictions<br/>2-5 Years"]
        end

        %% === STAGE 3: FINANCIAL PREDICTION ===
        subgraph STAGE_3 ["Financial Terms"]
            FINANCIAL_MODELS["Position Financial Models<br/>PyMC Bayesian"]
            FINANCIAL_PREDS["💰"]
        end
    end

    %% === STORAGE LAYER ===
    subgraph STORAGE ["💾 Storage (in DuckDB)"]
        FEATURES["Position Features<br/>"]
        RESULTS["🏆 Final Predictions<br/>Per Position"]
    end

    %% === CONNECTIONS ===
    %% Infrastructure → Data Flow
    DUCKDB -->|"Stores & Serves"| FEATURES
    DBT -->|"Transforms"| FEATURES
    K8S -->|"Orchestrates"| CLUSTERING
    K8S -->|"Deploys"| YEAR_MODELS
    K8S -->|"Deploys"| FINANCIAL_MODELS

    %% Data Pipeline Flow
    FEATURES --> CLUSTERING
    CLUSTERING --> ARCHETYPES
    ARCHETYPES --> YEAR_MODELS
    FEATURES --> YEAR_MODELS
    YEAR_MODELS --> YEAR_PREDS
    YEAR_PREDS --> FINANCIAL_MODELS
    ARCHETYPES --> FINANCIAL_MODELS
    FEATURES --> FINANCIAL_MODELS
    FINANCIAL_MODELS --> FINANCIAL_PREDS
    FINANCIAL_PREDS --> RESULTS

    %% === STYLES ===
    class INFRA,DUCKDB,K8S,DBT infra
    class STORAGE,FEATURES,RESULTS storage
    class STAGE_1 stage1
    class STAGE_2 stage2
    class STAGE_3 stage3
    class FEATURES features
    class CLUSTERING,YEAR_MODELS,FINANCIAL_MODELS model
    class ARCHETYPES,YEAR_PREDS,FINANCIAL_PREDS,RESULTS output;
```



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
    │   │       ├── elo_ratings.sql
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
    
