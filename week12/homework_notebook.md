# Homework

## Logging into the Server

Logon to our server **newton**.

- Username: your first name (all lowercase)  
- Password: `!{first name}2026`  
  - Example: `!glenn2026`  
  - ⚠️ This is a **bad password** (not secure) since it contains your username.

To log in:

```bash
ssh {first_name}@10.246.31.148
```

Once logged in, change your password:

```bash
passwd
```

👉 Remember your new password! If you forget, it can be reset.

---

## Accessing Shared Data

Test access to shared data:

```bash
ls -l /mnt/classdata
```

If this works, you can read data from **hal9000** just like from your laptop/desktop.

👉 This means:
- You can process data directly on the server
- No need to copy large datasets

---

## RSAM Notebook Exercise

Re-run your RSAM notebooks with two improvements:

### 1. Read extra time around each day

For example, for **2009-03-20**, use:

```python
starttime = UTCDateTime(2009, 3, 19, 23, 0, 0)
endtime   = UTCDateTime(2009, 3, 21, 1, 0, 0)
```

👉 This gives a **26-hour stream**, not 24 hours.

---

### 2. Pre-process the Stream before RSAM

Example:

```python
# remove best fit line
st.detrend('linear')

# fill gaps with last value
st.merge(method=1, fill_value='latest')

# remove DC offset
st.detrend('constant')

# taper edges (1 hour each side)
st.taper(max_percentage=1/26)

# high-pass filter (short-period)
st.filter('highpass', freq=0.5)

# trim to the day of interest
st.trim(starttime=day, endtime=day + 1)
```

Where:

```python
day = UTCDateTime(...)
```

---

## Workflow

1. Test on **1–3 days** locally
2. Convert notebook to script:

```bash
jupyter nbconvert --to script {your_notebook}.ipynb
```

This creates:

```bash
{your_notebook}.py
```

---

## Copy Files to Server

From your laptop:

```bash
scp myfile.py {first_name}@10.246.31.148:.
```

This copies the file to your home directory.

Then on **newton**:

```bash
mv myfile.py mydirectory/
```

---

## Final Step

Run your script on the server.

---

## Deadline

Please complete this exercise by **Thursday's class**.

---

## TO DO (Glenn)

- Setup global versions of:
  - `CompSciS26`
  - `flovopy`
- Create shared conda environment:
  - `flovopy_env`
