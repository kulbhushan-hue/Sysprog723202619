
import streamlit as st
import json, os, random, time
from pathlib import Path

st.set_page_config(page_title="MVS / TK5 Operations Practice", page_icon="🖥️", layout="wide")

ROOT = Path(__file__).parent
DOCS = ROOT.parent / "docs"
JCL = ROOT.parent / "jcl"

# ---------- State ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "system" not in st.session_state:
    st.session_state.system = {
        " IPL": False,
        "MASTER_CONSOLE": False,
        "LOGGED_ON": False,
        "USER": "",
        "DATASETS": {},
        "JOBS": {},
        "VTAM": "INACTIVE",
        "TCAS": "INACTIVE",
        "TSO": "INACTIVE",
        "SMPE": "READY",
        "DASD": {
            "WORK01": {"VOLSER":"WORK01","TYPE":"3390","FREE_CYL":2500,"USED_CYL":500},
            "SYSRES": {"VOLSER":"SYSRES","TYPE":"3390","FREE_CYL":1200,"USED_CYL":800}
        },
        "SYSMODS": {}
    }
if "quiz_idx" not in st.session_state:
    st.session_state.quiz_idx = 0
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

sys = st.session_state.system

def log(line, kind="info"):
    st.session_state.history.append({"text": line, "kind": kind})

def banner():
    log("IEA101A SPECIFY SYSTEM PARAMETERS FOR IPL", "msg")
    log("HCP000I TK5 SIMULATOR READY - MVS/ESA 370 MODE", "info")

def normalize(cmd):
    return " ".join(cmd.strip().upper().split())

# ---------- Console command engine ----------
def run_command(raw):
    cmd = normalize(raw)
    parts = cmd.split()
    if not parts:
        return
    verb = parts[0]

    if cmd in ("HELP", "?"):
        log("Supported: IPL, DISPLAY, D, VARY, V, START, S, STOP, P, MODIFY, F,")
        log("SEND, ROUCHE, LOGON, TSO, SUBMIT, SMPE, RECEIVE, APPLY, ACCEPT, CLEAR, EXIT")
        return

    if cmd == "CLEAR":
        st.session_state.history = []
        banner()
        return

    if cmd == "EXIT":
        log("LOGOFF AT 19:03:11 ON 10/19/26", "info")
        sys["LOGGED_ON"] = False
        sys["USER"] = ""
        return

    if verb in ("IPL", "S IPL"):
        sys["IPL"] = True
        log("IPL INFO: NUCLEUS LOAD FROM SYSRES", "info")
        log("IEA101A SPECIFY SYSTEM PARAMETERS FOR IPL", "msg")
        log("IEA321I MASTER SCHEDULER INITIALIZATION COMPLETE", "info")
        log("IEE252I DEVICE 0800 STATUS: ONLINE", "info")
        log("IEE043I A NEW SYSTEM LOG HAS BEEN STARTED", "info")
        return

    if verb in ("DISPLAY", "D"):
        target = parts[1] if len(parts) > 1 else ""
        if target in ("A,L", "ACTIVE"):
            log("IEE114I 19.03.11 ACTIVITY FRAME 1", "info")
            log("JOBS  M/S  TS USERS  SYSAS  IDLE  INITS  ACTIVE/MAX VTAM", "info")
            log("00000 00000 00000    00004  00000 00000    00000/00000 INACTIVE", "info")
        elif target == "DASD":
            for vol, d in sys["DASD"].items():
                log(f"IEE457I {vol}  UNIT=0800  TYPE={d['TYPE']}  VOLSER={d['VOLSER']}", "info")
                log(f"  FREE CYLINDERS={d['FREE_CYL']}  USED CYLINDERS={d['USED_CYL']}", "info")
        elif target == "TSO":
            log(f"IEE136I TSO STATUS: {sys['TSO']}", "info")
        elif target == "VTAM":
            log(f"IST097I VARY ACCEPTED - VTAM STATUS: {sys['VTAM']}", "info")
        elif target == "JOBS":
            if not sys["JOBS"]:
                log("IEE114I NO ACTIVE JOBS", "info")
            else:
                for j, s in sys["JOBS"].items():
                    log(f"JOB {j} STATUS={s}", "info")
        else:
            log("IEE342I INVALID DISPLAY REQUEST", "err")
        return

    if verb == "VARY":
        if len(parts) < 3:
            log("IEE342I INVALID VARY REQUEST", "err"); return
        obj = parts[1]; action = parts[2]
        if obj == "TSO":
            sys["TSO"] = "ACTIVE" if action == "ONLINE" else "INACTIVE"
            log(f"IEE136I TSO STATUS: {sys['TSO']}", "info")
        elif obj == "VTAM":
            sys["VTAM"] = "ACTIVE" if action == "ONLINE" else "INACTIVE"
            log(f"IST097I VARY ACCEPTED - VTAM STATUS: {sys['VTAM']}", "info")
        elif obj in sys["DASD"]:
            log(f"IEE612I DEVICE {obj} {action}", "info")
        else:
            log("IEE342I INVALID VARY TARGET", "err")
        return

    if verb in ("START", "S"):
        if len(parts) > 1 and parts[1] == "TSO":
            sys["TSO"] = "ACTIVE"
            log("IEE136I TSO STATUS: ACTIVE", "info")
        elif len(parts) > 1 and parts[1] == "VTAM":
            sys["VTAM"] = "ACTIVE"
            log("IST099I VTAM INITIALIZATION COMPLETE", "info")
        else:
            log("IEE342I INVALID START COMMAND", "err")
        return

    if verb in ("STOP", "P"):
        if len(parts) > 1 and parts[1] == "TSO":
            sys["TSO"] = "INACTIVE"
            log("IEE136I TSO STATUS: INACTIVE", "info")
        else:
            log("IEE342I INVALID STOP COMMAND", "err")
        return

    if verb in ("MODIFY", "F"):
        log("IEE342I MODIFY COMMAND ACCEPTED BY SIMULATOR", "info")
        return

    if verb == "SEND":
        log("IEE712I MESSAGE SENT TO ALL ACTIVE TERMINALS", "info")
        return

    if verb == "LOGON":
        user = parts[1] if len(parts) > 1 else "IBMUSER"
        if not sys["TSO"]:
            log("IKJ56700I TSO IS NOT ACTIVE", "err"); return
        sys["LOGGED_ON"] = True
        sys["USER"] = user
        log(f"LOGON IN PROGRESS AT 19:03:11", "info")
        log(f"IKJ56947I FILE EDIT UTILITY - USER {user} LOGGED ON", "info")
        log("READY", "prompt")
        return

    if verb == "SUBMIT":
        if len(parts) < 2:
            log("IKJ56701A MISSING MEMBER NAME", "err"); return
        member = parts[1]
        sys["JOBS"][member] = "RUNNING"
        log(f"IKJ56225I JOB {member} SUBMITTED", "info")
        log(f"$HASP100 {member} ON INTRDR", "info")
        log(f"$HASP375 {member} ESTIMATED 100 CARDS", "info")
        sys["JOBS"][member] = "ENDED"
        log(f"$HASP395 {member} ENDED", "info")
        return

    if verb == "SMPE":
        log("GIM20501I SMP/E IS READY", "info")
        return

    if verb in ("RECEIVE", "APPLY", "ACCEPT"):
        if len(parts) < 2:
            log("GIM20502I MISSING SYSMOD ID", "err"); return
        sid = parts[1]
        sys["SYSMODS"][sid] = {"RECEIVE": "APPLIED", "APPLY": "APPLIED", "ACCEPT": "ACCEPTED"}[verb]
        log(f"GIM20501I {verb} PROCESSING COMPLETE FOR {sid}", "info")
        return

    if verb == "ALLOC":
        log("IKJ56228I DATA SET ALLOCATED", "info")
        return

    log(f"IEE342I UNRECOGNIZED OR UNSUPPORTED COMMAND: {cmd}", "err")

# ---------- UI ----------
st.title("🖥️ MVS / TK5 Operations Practice Simulator")
st.caption("A browser-based practice console inspired by MVS/ESA and TK5. For training only—not a real mainframe.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Console", "Walkthrough", "SMPE JCL", "Q & A", "Files"]
)

with tab1:
    c1, c2 = st.columns([3,1])
    with c1:
        st.subheader("Master Console / TSO Simulation")
        with st.container(height=430):
            for h in st.session_state.history:
                color = {"info":"#d6e4ff","msg":"#fff3cd","err":"#f8d7da","prompt":"#d1e7dd"}.get(h["kind"], "#f8f9fa")
                st.markdown(
                    f"<div style='font-family:monospace;background:{color};padding:4px 8px;border-radius:4px;margin-bottom:3px'>{h['text']}</div>",
                    unsafe_allow_html=True
                )
        cmd = st.text_input("Enter console or TSO command", placeholder="IPL  |  D A,L  |  V TSO,ONLINE  |  LOGON IBMUSER  |  SUBMIT MYJOB")
        colA, colB, colC = st.columns([1,1,8])
        if colA.button("Run", type="primary"):
            run_command(cmd)
            st.rerun()
        if colB.button("Clear"):
            st.session_state.history = []
            banner()
            st.rerun()
    with c2:
        st.subheader("System State")
        st.metric("IPL", "Complete" if sys["IPL"] else "Not performed")
        st.metric("TSO", sys["TSO"])
        st.metric("VTAM", sys["VTAM"])
        st.metric("SMPE", sys["SMPE"])
        st.metric("User", sys["USER"] or "None")
        st.subheader("Quick Commands")
        for q in ["IPL", "D A,L", "D DASD", "V TSO,ONLINE", "S VTAM", "LOGON IBMUSER", "SUBMIT MYJOB", "SMPE", "RECEIVE UZ00001", "APPLY UZ00001", "ACCEPT UZ00001", "HELP"]:
            if st.button(q, use_container_width=True):
                run_command(q)
                st.rerun()

with tab2:
    st.subheader("Guided Operations Walkthrough")
    st.markdown((DOCS / "walkthrough.md").read_text())

with tab3:
    st.subheader("Simulated SMP/E JCL — Dummy SYSMOD")
    st.info("These JCL members use a fictitious SYSMOD ID `UZ00001` and dummy libraries. Do not run them on a production system.")
    for f in sorted(JCL.glob("*.jcl")):
        with st.expander(f.name):
            st.code(f.read_text(), language="jcl")

with tab4:
    st.subheader("Operations Practice Questions")
    qa = json.loads((DOCS / "qa.json").read_text())
    idx = st.session_state.quiz_idx
    if idx < len(qa):
        q = qa[idx]
        st.markdown(f"**Q{idx+1}. {q['question']}**")
        choice = st.radio("Select an answer", q["options"], key=f"q{idx}")
        if st.button("Check answer"):
            if choice == q["answer"]:
                st.success("Correct! " + q["explanation"])
                st.session_state.quiz_score += 1
            else:
                st.error("Incorrect. " + q["explanation"])
        if st.button("Next question"):
            st.session_state.quiz_idx += 1
            st.rerun()
    else:
        st.success(f"Practice complete. Score: {st.session_state.quiz_score}/{len(qa)}")
        if st.button("Restart quiz"):
            st.session_state.quiz_idx = 0
            st.session_state.quiz_score = 0
            st.rerun()

with tab5:
    st.subheader("Deployment Files")
    st.markdown("""
    - `app/app.py` — Streamlit application  
    - `requirements.txt` — Python dependencies  
    - `docs/walkthrough.md` — operator walkthrough  
    - `docs/qa.json` — practice questions  
    - `jcl/*.jcl` — simulated SMP/E JCL examples  
    - `.streamlit/config.toml` — optional theme  
    """)
    st.markdown("**Streamlit Cloud deployment**")
    st.code("""
1. Upload this project to a GitHub repository.
2. In Streamlit Community Cloud, choose New app.
3. Select the repository and branch.
4. Set Main file path to: app/app.py
5. Deploy.
    """)
