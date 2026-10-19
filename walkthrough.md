# MVS / TK5 Operations Walkthrough

## 1. Start the simulator
Open the app and use the **Console** tab.

## 2. Perform an IPL
Enter:

```text
IPL
```

Expected simulator response:
- Nucleus load message
- `IEA101A` prompt
- Master scheduler initialization
- System log started

In real MVS, IPL initializes the operating system, loads the nucleus, builds system control blocks, and starts required address spaces.

## 3. Display system activity

```text
D A,L
```

This requests active jobs, started tasks, TSO users, and system address spaces.

## 4. Display DASD volumes

```text
D DASD
```

The simulator shows volume serial, device type, and free/used cylinders.

## 5. Start TSO and VTAM

```text
V TSO,ONLINE
S VTAM
```

Then log on:

```text
LOGON IBMUSER
```

## 6. Submit a batch job

```text
SUBMIT MYJOB
```

The simulator emulates JES submission and completion messages.

## 7. Practice SMP/E
Use the **SMPE JCL** tab to review the dummy SYSMOD examples. Then enter:

```text
SMPE
RECEIVE UZ00001
APPLY UZ00001
ACCEPT UZ00001
```

## 8. Useful commands
- `HELP` — list supported commands
- `D TSO` — display TSO status
- `D VTAM` — display VTAM status
- `D JOBS` — display simulated jobs
- `CLEAR` — clear console
- `EXIT` — log off
