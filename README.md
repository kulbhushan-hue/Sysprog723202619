# MVS / TK5 Operations Practice Simulator

A Streamlit-based training simulator for MVS console operations, TSO-style commands, batch-job submission, and dummy SMP/E SYSMOD processing.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## Deploy to Streamlit Community Cloud

1. Push this folder to GitHub.
2. Create a new Streamlit app.
3. Set **Main file path** to `app/app.py`.
4. Deploy.

## Important

This is an educational simulator. It does not connect to a real mainframe, z/OS system, TK5 installation, or SMP/E environment. The JCL examples use fictitious names and a dummy SYSMOD ID, `UZ00001`.
