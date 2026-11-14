# Start here — Topic 47 Codex handoff

You already have the real outputs of the Colab run. **No retraining or redownloading the 226 MB PBF is necessary to build the dashboard.**

Contents:

- `Topic47_Colab_GPU_Executed.ipynb` — executed notebook and visualizations.
- `outputs/` — preprocessed tables, SQLite DB, trained model, DBSCAN clusters, and reports.
- `CODEX_CONTEXT.md` — detailed specification and university grading rubric.
- `TRAINING_RESULTS.md` — measured results transcribed from the uploaded data archive.
- `CODEX_PROMPT.txt` — single ready-to-paste command for Codex.

## Use

1. Extract this ZIP into a new local project folder.
2. Open a terminal in **this folder**, then run `codex` (with Codex CLI installed and configured).
3. Paste the contents of `CODEX_PROMPT.txt` into Codex.
4. After it implements the app, review tests and run `streamlit run app.py`.
5. Commit/push your app to GitHub once you have reviewed it. Do **not** commit raw PBF files or falsely claim features or tests exist before Codex runs them.

## Outputs already supplied

`outputs/kazakhstan_poi.sqlite` — 126,778 POI rows, 20 regions, 10 categories; `outputs/urban_autoencoder.pt` — GPU-trained PyTorch state_dict; `outputs/poi_enriched.parquet` — map points; `outputs/clusters.parquet` — DBSCAN city clusters. All files are real outputs uploaded from Colab.
