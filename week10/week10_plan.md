# Week 8 Plan

1. Network detection of Redoubt microquakes
2. Network detection of rocket launches
3. Do both with ObsPy and Antelope
4. RSAM of the Redoubt sequence. Maybe the rocket sequence too. So we can update the 110_RSAM notebook.
5. Event classification? And magnitude? Probably next week

Which of these do I do as a homework exercise?

This might be the week to switch everyone to FLOVOPY repository

So then everyone would build that environment. 

Might be time to pick a project too.
Each student should probably just pick a dataset (swarm, aftershock sequence, eruption sequence) and then apply similar processing to it:
1. RSAM
2. Reduced displacement
3. Pensive or flovopy spectrograms
4. Energy magnitude per minute or hour or day
5. Frequency analysis of continuous data
6. Single station detections & simple timewindow association
7. Network detections & associations
8. Counts per unit time
9. Amplitude source location of events
10. Frequency analysis of events
11. Event classification?


Yes — that is a very good homework exercise. It is realistic, teaches judgment, and makes students confront the fact that detection is a tuning problem, not a button press.

I would make the homework:

Week 10 Homework: Calibrating STA/LTA Event Detection

Students manually identify a small set of events first, then use those labels as a reference to tune STA/LTA parameters for both a single station and a network detector.

That gives them both skills without making the assignment explode.

Core learning goals

They should learn to:
	•	identify event windows manually
	•	understand what STA/LTA parameters actually do
	•	quantify detector performance
	•	compare single-station and network detection
	•	see that “optimal” depends on the scoring function

A reasonable assignment structure

Use one manageable time window, not several days. Something like 1–3 hours of Redoubt or Montserrat data is enough.

Part A. Manual picking

Have each student:
	•	inspect a continuous time window
	•	identify perhaps 8–15 events manually
	•	record:
	•	event start time
	•	event end time
	•	maybe peak time
	•	maybe confidence level

This can be done in ObsPy plots, Swarm, or dbpick if you want to expose Antelope. For grading and reproducibility, I would require the final picks in a CSV or DataFrame regardless of what tool they used to make them.

A simple schema:
	•	event_id
	•	t_start
	•	t_end
	•	t_peak optional
	•	station for single-station picks
	•	notes optional

Part B. Single-station STA/LTA tuning

Then they choose one station and test a grid of parameters, for example:
	•	STA: 0.5, 1, 2, 3 s
	•	LTA: 5, 10, 20, 30 s
	•	on threshold: 2, 3, 4
	•	off threshold: 1.2, 1.5, 2

That is already a lot of combinations, so you may want to constrain it further.

For each parameter set, they generate detections and compare them to the manual catalog.

Part C. Network tuning

Then repeat with network coincidence triggering using a smaller parameter search. For example:
	•	coincidence sum: 2, 3, 4 stations
	•	trigger-on and trigger-off inherited from station settings
	•	maybe require similar stations each time

This keeps network detection from becoming a second full assignment.

⸻

The scoring system

You want something that rewards:
	•	matching manual start/end times
	•	detecting real events
	•	avoiding false detections

That means you need two levels of scoring:

1. Event matching score

First match automatic detections to manual events.

A reasonable rule is:

An automatic detection matches a manual event if their windows overlap, or if the automatic trigger start is within some tolerance of the manual start, such as 2–5 seconds.

Then classify each automatic detection as:
	•	TP true positive: matched to one manual event
	•	FP false positive: unmatched automatic detection
	•	FN false negative: manual event with no automatic match

This gives the classic counts.

2. Timing error score

For matched events, compute timing errors:
	•	start-time error:
e_s = t_{start}^{auto} - t_{start}^{manual}
	•	end-time error:
e_e = t_{end}^{auto} - t_{end}^{manual}

Then compute RMS timing error over matched events:

\mathrm{RMSE}_{time} = \sqrt{\frac{1}{2N_{TP}} \sum (e_s^2 + e_e^2)}

This gives the least-squares flavour you want.

⸻

Recommended overall score

I would not use timing error alone. A detector that finds only 2 perfect events out of 15 would look artificially good.

A good combined score is:

Option A: simple weighted score

\mathrm{Score} = F1 - \alpha \cdot \mathrm{RMSE}_{time}

Where:
	•	F1 is the harmonic mean of precision and recall
	•	RMSE is in seconds
	•	\alpha is a small weight, maybe 0.02 to 0.1 depending on your time scale

This is intuitive:
	•	higher F1 is better
	•	lower timing error is better

Option B: separate metrics

Honestly, for teaching, this may be better:

Have them report:
	•	Precision
	•	Recall
	•	F1
	•	Mean or RMS start-time error
	•	Mean or RMS end-time error

Then define the “best” detector as:
	•	highest F1
	•	among similarly high-F1 solutions, lowest timing error

Pedagogically, this is cleaner than hiding everything in one number.

Option C: explicit penalty function

If you want one least-squares-like objective:

J = w_1 \cdot FN + w_2 \cdot FP + w_3 \sum e_s^2 + w_4 \sum e_e^2

Minimize J.

This is elegant, but students may find it less intuitive unless you walk them through it.

A reasonable choice might be:
	•	w_1 = 5
	•	w_2 = 2
	•	w_3 = 1
	•	w_4 = 1

That says missing real events is worse than having extra detections.

For undergrads or mixed-level grad students, I would still prefer Option B or A.

⸻

My recommendation for your class

Use this:

Primary detector score
	1.	Match detections to manual events
	2.	Compute:
	•	precision
	•	recall
	•	F1
	•	RMS start error
	•	RMS end error

Ranking rule

Choose the “best” parameter set as the one with:
	•	highest F1
	•	and, among those within say 5% of the best F1, smallest timing RMSE

That is scientifically reasonable and easy to explain.

⸻

What makes a match?

You need to define that clearly.

I would say:

An automatic detection matches a manual event if either:
	•	the two time windows overlap by at least some minimum amount, or
	•	the automatic start time lies within, say, 3 seconds of the manual start

For longer emergent volcanic signals, overlap is probably the better rule.

A nice metric is intersection-over-union for time windows:

IoU = \frac{\text{overlap duration}}{\text{union duration}}

Then declare a match if IoU > 0.2 or 0.3.

That is elegant, though perhaps a bit advanced. Simpler overlap criteria may be enough.

⸻

Reasonable homework scope

To keep this doable, I would assign:

Required
	•	manually label 10 events in one time window
	•	tune a single-station STA/LTA detector
	•	compute precision, recall, F1, and timing errors
	•	discuss tradeoffs

Strongly recommended / optional extension
	•	run a network detector on the same interval
	•	compare single-station vs network performance

That way everyone masters single-station, and better students push into network detection.

If you make both required, keep the window short.

⸻

Suggested deliverables

Students submit:
	•	notebook
	•	CSV of manual picks
	•	table of tested parameter combinations and scores
	•	one plot showing manual and automatic windows
	•	short discussion:
	•	best parameter set
	•	tradeoff between false positives and missed events
	•	comparison of single-station and network detection

⸻

A very workable grading design

Something like:
	•	20% manual picks clearly documented
	•	25% parameter sweep implemented correctly
	•	20% scoring metrics computed correctly
	•	20% plots and comparison of results
	•	15% interpretation and discussion

If you want, you could add a bonus for network detection.

⸻

Best pedagogical framing

I would present the assignment as:

Build a detector that best reproduces a small manually constructed catalog.

That sounds like real observatory work, because it is.

⸻

My practical recommendation

For this week, I would make:

Homework 10

Required: single-station calibration and scoring
Bonus or part 2: network coincidence detection on the same interval

Then next week you can build naturally to:
	•	event rate
	•	RSAM
	•	reduced displacement
	•	frequency features
	•	classification

That gives the course a very coherent arc.

I can draft the exact assignment sheet and a model scoring function in Python.


This is a great moment in the course—you’re transitioning from “learning tools” to “doing observatory-style seismology.” I’ll lay this out as a clean, teachable Week 10 plan, a concrete homework, and then a forward-looking roadmap so students see where they’re heading.

⸻

🌋 Week 10 Theme

From Detection to Calibration

“Anyone can run STA/LTA. A seismologist knows how to tune it.”

This week is about:
	•	moving from single-station → network detection
	•	introducing manual catalog vs automated detection
	•	teaching that detection is an optimization problem

⸻

📚 Week 10 Class Plan

🔹 Class 1 — Network Detection (Redoubt)

Goals
	•	Introduce coincidence triggering
	•	Show why single-station detection fails in noisy data

Flow

1. Conceptual intro (10–15 min)
	•	False positives in single-station STA/LTA
	•	Network logic:
	•	“real events appear on multiple stations”
	•	Introduce coincidence sum

2. Live coding (30–40 min)
	•	Load Redoubt data (short window, e.g., 1–2 hours)
	•	Run:
	•	single-station STA/LTA
	•	network coincidence_trigger

3. Visual comparison (15 min)
	•	Plot detections vs waveform
	•	Show:
	•	missed events
	•	false detections
	•	improved robustness

Key takeaway

Detection quality depends on both parameters and network geometry

⸻

🔹 Class 2 — Manual Picking & Detector Calibration

Goals
	•	Introduce manual event definition
	•	Frame STA/LTA tuning as a data-fitting problem

Flow

1. Manual picking demo (20 min)
	•	Use ObsPy plots (or dbpick optionally)
	•	Identify:
	•	start
	•	end
	•	ambiguous cases

2. Define the problem (20 min)

“Given a manual catalog, how do we build a detector that reproduces it?”

Introduce:
	•	True positives (TP)
	•	False positives (FP)
	•	False negatives (FN)

3. Introduce scoring (20 min)

Explain:
	•	Precision = TP / (TP + FP)
	•	Recall = TP / (TP + FN)
	•	F1 score

Then timing:
	•	start/end error
	•	RMS timing error

4. Show parameter sweep (optional demo)
	•	Vary STA, LTA, thresholds
	•	Show tradeoffs:
	•	sensitive vs noisy
	•	strict vs missing events

Key takeaway

Detection is a tradeoff between sensitivity and reliability

⸻

🔹 Class 3 — Real-World Signals + FLOVOPY Intro

Goals
	•	Broaden perspective beyond earthquakes
	•	Introduce course infrastructure shift

Flow

1. Rocket launch example (20–30 min)
	•	Show signals from Jan–Mar 2026
	•	Compare to Redoubt:
	•	emergent vs impulsive
	•	frequency differences

👉 Key message:

“Not all seismic signals are earthquakes”

⸻

2. FLOVOPY introduction (20–30 min)
	•	Show repo structure
	•	Explain:
	•	reusable workflows
	•	modular design
	•	Demo one useful function (e.g., RSAM or detection wrapper)

⚠️ Do NOT fully migrate yet—just introduce.

⸻

3. Project preview (10–15 min)

Tell students:

“You are about to start your own observatory-style analysis.”

Introduce the processing stack (see below).

⸻

📝 Week 10 Homework

🎯 Title

Calibrating STA/LTA Event Detection

⸻

Task Overview

Students will:
	1.	Manually identify ~10 events in a short dataset
	2.	Run STA/LTA detection with multiple parameter sets
	3.	Compare detections to manual picks
	4.	Quantify performance
	5.	(Optional) extend to network detection

⸻

🔹 Part A — Manual Picks
	•	Select ~1–2 hours of data
	•	Identify ~10 events
	•	Record:
	•	start time
	•	end time

⸻

🔹 Part B — Single-Station Detection
	•	Choose one station
	•	Test several parameter combinations:
	•	STA window
	•	LTA window
	•	trigger-on
	•	trigger-off

⸻

🔹 Part C — Scoring

For each parameter set:

Compute:
	•	TP, FP, FN
	•	Precision, Recall, F1
	•	RMS start-time error
	•	RMS end-time error

⸻

🔹 Part D — Select Best Detector

Define best as:
	•	highest F1
	•	among similar F1, lowest timing error

⸻

🔹 Part E — Discussion

Students explain:
	•	tradeoffs they observed
	•	why their chosen parameters are “best”
	•	limitations of STA/LTA

⸻

🔹 Optional Extension (recommended for stronger students)
	•	Run network coincidence detection
	•	Compare performance to single-station

⸻

📦 Deliverables
	•	Notebook
	•	CSV of manual picks
	•	Table of parameter results
	•	2–3 plots:
	•	waveform + detections
	•	event rate
	•	Short written interpretation

⸻

🚀 Where the Course Goes Next (Weeks 11–13)

Now we build a full observatory pipeline.

⸻

🔹 Week 11 — Continuous Metrics (RSAM & Beyond)

Topics:
	•	RSAM (core observatory metric)
	•	Reduced displacement (conceptually)
	•	Time series of activity

Outcome:

Students can answer:

“How active is the volcano over time?”

⸻

🔹 Week 12 — Event Characterization

Topics:
	•	Spectrograms (Pensive / FLOVOPY)
	•	Frequency content
	•	Energy metrics
	•	Event features

Outcome:

Students can answer:

“What kind of events are these?”

⸻

🔹 Week 13 — Event Catalogs & Classification

Topics:
	•	Feature extraction
	•	Rule-based classification
	•	Intro to clustering / ML

Outcome:

Students can answer:

“How many types of events are there?”

⸻

🔹 Week 14+ — Projects

Students apply the full stack to a dataset:

🔥 Processing Stack
	1.	Continuous data exploration
	2.	RSAM / amplitude metrics
	3.	STA/LTA detection
	4.	Network detection
	5.	Event rate analysis
	6.	Spectrograms
	7.	Feature extraction
	8.	Source metrics (reduced displacement, energy)
	9.	Classification

⸻

🌋 Montserrat Transition

Perfect timing:
	•	Week 10–11: Redoubt (clean dataset)
	•	Week 11–12: Introduce Montserrat
	•	Weeks 12+: full projects using Montserrat or other datasets

👉 This creates a powerful contrast:
	•	textbook vs real-world messy data

⸻

🧭 Final Framing to Students

You might say something like:

“Up to now, you’ve been learning tools.
From this point on, you’re building a monitoring system.”

And:

“By the end of this course, you will be able to take raw seismic data from a volcano and turn it into scientific insight.”

⸻

👍 Final Thoughts

This is an excellent pivot point in your course.

You’re now aligning perfectly with:
	•	your MVO/AVO experience
	•	real observatory workflows
	•	modern reproducible science (FLOVOPY)

⸻

If you want, I can next:
	•	draft the exact notebook for the homework
	•	provide a starter scoring function (Python)
	•	or design the Week 11 RSAM lab using FLOVOPY


    ========

Yes — this is a very strong move, and honestly a better narrative than what you had before.

You’re essentially flipping the course from:

detection → analysis

to:

monitoring → detection → analysis

That mirrors how observatories actually work.

⸻

🌋 New Framing for Week 10

Theme:

“How do we monitor a volcano in real time?”

Instead of starting with detection, you start with:
	•	continuous data
	•	situational awareness
	•	operational tools

👉 This is exactly how MVO/AVO actually operate.

⸻

🧭 Why This Is the Right Pivot

1. It matches real observatory workflow

In reality:
	•	You look at RSAM / spectrograms first
	•	Then ask: “what events are happening?”

Not the other way around.

⸻

2. It gives students intuition

Before tuning STA/LTA, they need to see:
	•	what a swarm looks like
	•	how tremor evolves
	•	how frequency content changes

Otherwise detection is abstract.

⸻

3. It sets up everything that follows

This naturally leads to:
	•	RSAM → activity rate
	•	Spectrograms → signal type
	•	Detection → event extraction
	•	Classification → interpretation

⸻

📚 Tomorrow’s Class Plan (Revised)

🎯 Title:

Continuous Monitoring of a Volcanic Sequence (Redoubt 2009)

⸻

🔹 Part 1 — Big Picture (10–15 min)

Start with something like:

“Imagine you are on shift at a volcano observatory. What do you look at first?”

Then introduce:

Core monitoring tools:
	•	RSAM
	•	Spectrograms
	•	Reduced displacement
	•	Energy / amplitude metrics

👉 Emphasize:

These are continuous data products, not event-based.

⸻

🔹 Part 2 — Introduce FLOVOPY (15–20 min)

Keep it practical, not overwhelming.

Show:
	•	repo structure
	•	where monitoring tools live
	•	how this replaces ad-hoc notebooks

Do:
	•	clone repo (or have them do it live if feasible)
	•	briefly show environment setup

👉 Don’t get bogged down — this is orientation, not mastery.

⸻

🔹 Part 3 — Continuous Data Exploration (Main Block)

Use Redoubt March 20–23, 2009.

⸻

1. SWARM-style visualization (15–20 min)
	•	helicorder/dayplot style
	•	multiple stations

👉 Ask:
	•	when does activity increase?
	•	are there bursts or steady tremor?

⸻

2. RSAM (15–20 min)
	•	compute RSAM
	•	plot vs time

👉 Highlight:
	•	eruption precursors
	•	swarm evolution

👉 Key idea:

RSAM = “how loud is the volcano over time?”

⸻

3. Spectrograms (Pensive-style) (15–20 min)
	•	generate spectrograms
	•	scroll through time

👉 Ask:
	•	how does frequency content evolve?
	•	can you distinguish event types?

👉 Key idea:

Frequency = physics of the source

⸻

4. Reduced Displacement / Energy (15–20 min)
	•	introduce concept (don’t over-derive)
	•	compute time series

👉 Emphasize:
	•	source size proxy
	•	comparability across stations

⸻

5. Frequency Metrics (10–15 min)
	•	peak frequency
	•	mean frequency

👉 Connect to:
	•	event classification (preview of next weeks)

⸻

🔹 Part 4 — Wrap-Up (10 min)

Tie it together:

“Before we detect events, we need to understand the continuous signal.”

Then preview:
	•	next class: event detection + calibration
	•	eventual goal: build a catalog + classify events

⸻

🧠 Key Concept to Emphasize

This is the core message of the day:

Detection is just one layer of a monitoring system.

The hierarchy is:
	1.	Continuous monitoring (RSAM, spectrograms)
	2.	Detection (STA/LTA)
	3.	Catalog building
	4.	Interpretation

⸻

📝 Homework Adjustment (Important)

Now that you’ve reframed the week:

Option A (best):

Keep the STA/LTA calibration homework, but:

👉 Require students to:
	•	first explore the data using RSAM/spectrograms
	•	then pick events

⸻

Option B (lighter transition):

Make this week:

Homework 10:
	•	compute RSAM
	•	generate spectrograms
	•	describe activity evolution

Then:

Homework 11:
	•	STA/LTA calibration

⸻

My recommendation:

Stick with your original plan but add:

“Use RSAM and spectrograms to guide your manual picks.”

That ties both worlds together nicely.

⸻

🚀 How This Sets Up the Next Weeks

This pivot actually makes the rest of your course much cleaner.

⸻

Week 10 (now)

Continuous monitoring
	•	RSAM
	•	spectrograms
	•	reduced displacement
	•	FLOVOPY intro

⸻

Week 11

Detection & calibration
	•	STA/LTA tuning
	•	network detection
	•	scoring system

⸻

Week 12

Event characterization
	•	spectrograms (event-based)
	•	feature extraction
	•	frequency metrics

⸻

Week 13

Classification
	•	rule-based classification
	•	intro to ML
	•	Montserrat dataset

⸻

Weeks 14+

Projects
	•	full observatory pipeline

⸻

🌋 When to Introduce Montserrat

Perfect transition:

After students understand:
	•	RSAM
	•	spectrograms
	•	detection

👉 Then say:

“Now let’s look at a real messy dataset.”

That’s when Montserrat lands.

⸻

⚖️ One Small Warning

This is a rich class — very easy to overload.

So:
	•	don’t try to fully explain reduced displacement physics
	•	don’t derive energy magnitude equations
	•	focus on interpretation and use

👉 Depth comes later.

⸻

👍 Final Verdict

This is a better structure than your original plan.

You’re now teaching:

“How to think like an observatory seismologist”

instead of:

“How to run detection algorithms”

⸻

If you want, I can:
	•	sketch the exact notebook structure for this class
	•	or help you design a clean RSAM + spectrogram FLOVOPY demo workflow
	•	or prepare a Montserrat transition lecture (which could be brilliant here)



This is a perfect place to anchor the course. What you want is a notebook that feels like:

“You’ve just walked into the Operations Room at a volcano observatory—what do you look at first?”

Below is a clean, teachable notebook outline that blends observatory realism with reproducible workflows (and sets up everything that follows).

⸻

🌋 Notebook Title

Continuous Monitoring of Volcanic Activity (Redoubt, March 2009)

⸻

🧭 0. Framing (Markdown)

Start with context, not code.

Purpose:
	•	Introduce continuous data monitoring tools
	•	Understand volcanic activity before event detection

Learning goals:
	•	Visualize continuous seismic data
	•	Compute RSAM
	•	Generate spectrograms
	•	Explore frequency and amplitude evolution
	•	Introduce reduced displacement / energy concepts

Narrative:

“You are on shift at a volcano observatory. Your job is to assess what the volcano is doing in real time.”

⸻

⚙️ 1. Setup

1.1 Imports

import obspy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from obspy.clients.fdsn import Client

(Optionally FLOVOPY imports if ready)

⸻

1.2 Define Time Window

t0 = obspy.UTCDateTime("2009-03-20")
t1 = obspy.UTCDateTime("2009-03-23")


⸻

1.3 Select Stations

network = "AV"
stations = ["REF", "RSO", "NCT"]  # example
channel = "BHZ"
client = Client("IRIS")  # or EARTHSCOPE


⸻

1.4 Load Data

st = obspy.Stream()

for sta in stations:
    try:
        st += client.get_waveforms(network, sta, "*", channel, t0, t1)
    except:
        print(f"Failed for {sta}")
        
st.merge()


⸻

📈 2. First Look: “SWARM-style” Visualization

2.1 Dayplot (Helicorder-style)

st.plot(type="dayplot", interval=60, right_vertical_labels=False)


⸻

2.2 Discussion (Markdown)

Prompt students:
	•	When does activity increase?
	•	Are signals impulsive or emergent?
	•	Do all stations see the same thing?

⸻

🔊 3. RSAM — Real-Time Seismic Amplitude Measurement

3.1 Concept (Markdown)

Explain briefly:

RSAM = average amplitude over time window
Used for tracking volcanic activity levels

⸻

3.2 Compute RSAM

def compute_rsam(tr, win=60):
    tr = tr.copy().detrend().filter("bandpass", freqmin=1, freqmax=10)
    data = np.abs(tr.data)
    
    n = int(win * tr.stats.sampling_rate)
    rsam = np.array([data[i:i+n].mean() for i in range(0, len(data)-n, n)])
    
    times = [tr.stats.starttime + i*win for i in range(len(rsam))]
    return times, rsam


⸻

3.3 Plot RSAM

for tr in st:
    t, r = compute_rsam(tr)
    plt.plot(t, r, label=tr.id)

plt.legend()
plt.ylabel("RSAM")
plt.xlabel("Time")
plt.title("RSAM vs Time")
plt.show()


⸻

3.4 Interpretation (Markdown)

Ask:
	•	When does RSAM increase?
	•	Is the increase gradual or sudden?
	•	What might this indicate physically?

⸻

🎧 4. Spectrograms (Pensive-style Exploration)

4.1 Generate Spectrogram

tr = st[0].copy()
tr.spectrogram(log=True, wlen=5, per_lap=0.9)


⸻

4.2 Discussion

Prompt:
	•	What frequency bands dominate?
	•	Do you see harmonic tremor?
	•	How does frequency evolve over time?

⸻

4.3 Optional: Sliding Spectrogram / Zoom

Encourage students to:
	•	zoom into specific time windows
	•	compare quiet vs active periods

⸻

📉 5. Frequency Metrics

5.1 Compute Simple Metrics

from scipy.fft import rfft, rfftfreq

def peak_frequency(tr):
    tr = tr.copy().detrend()
    yf = np.abs(rfft(tr.data))
    xf = rfftfreq(len(tr.data), 1/tr.stats.sampling_rate)
    return xf[np.argmax(yf)]


⸻

5.2 Apply Over Time Windows

(Short windows, e.g. 10–30 seconds)

⸻

5.3 Plot Frequency Evolution

# pseudo-loop over windows


⸻

5.4 Interpretation
	•	Does dominant frequency change with activity?
	•	Are there distinct regimes?

⸻

📏 6. Reduced Displacement (Conceptual + Light Implementation)

6.1 Concept (Markdown)

Keep it simple:

Reduced displacement normalizes amplitude by distance and instrument effects
Gives a proxy for source strength

⸻

6.2 Simple Proxy (no full derivation)

def reduced_displacement(tr, r_km=5):
    # simplified proxy
    tr = tr.copy().detrend().filter("bandpass", freqmin=1, freqmax=10)
    return np.sqrt(np.mean(tr.data**2)) * r_km


⸻

6.3 Plot Over Time

Same structure as RSAM

⸻

6.4 Interpretation
	•	Compare with RSAM
	•	Which better reflects “source strength”?

⸻

⚡ 7. Energy / Amplitude Metrics

7.1 Concept

Energy scales with amplitude² and duration

⸻

7.2 Simple Energy Estimate

def energy(tr):
    return np.sum(tr.data**2)


⸻

7.3 Time Series of Energy

Windowed like RSAM

⸻

7.4 Discussion
	•	Do energy spikes correspond to visible events?
	•	How does energy relate to RSAM?

⸻

🔁 8. Bringing It Together

8.1 Multi-panel Plot

Combine:
	•	RSAM
	•	frequency
	•	energy

👉 show them together vs time

⸻

8.2 Interpretation Questions
	•	When does the eruption sequence intensify?
	•	Are there precursors?
	•	Do all metrics tell the same story?

⸻

🔮 9. Transition to Event Detection

Markdown (very important)

This is where you pivot the course:

“So far, we’ve looked at continuous data.
But often we want to extract discrete events from this signal.”

Introduce:
	•	STA/LTA
	•	event catalogs
	•	network detection

⸻

🧪 10. Optional Exploration Cells

Give students room to play:
	•	try different filters
	•	compare stations
	•	zoom into interesting windows

⸻

📌 11. Summary

Key takeaways:
	•	Continuous monitoring is the first layer of observatory analysis
	•	RSAM tracks activity level
	•	Spectrograms reveal signal type
	•	Frequency + amplitude give physical insight
	•	Detection is built on top of this foundation

⸻

💡 Design Philosophy (for you)

This notebook does several important things:

1. Feels like real operations

Students are interpreting, not just coding

2. Builds intuition first

Before algorithms

3. Sets up next notebook perfectly

Next step becomes:

“Now let’s detect and catalog events from this signal”

⸻

🚀 Optional Enhancement (Very You)

You could add a short section:

“What would you report in an observatory log?”

Have students write:
	•	“Activity increased at X time”
	•	“Dominant frequency shifted from A to B”
	•	“Possible onset of tremor”

👉 This ties directly to your MVO experience and makes it real.

⸻

If you want, I can next:
	•	turn this into a fully runnable notebook
	•	integrate it directly with FLOVOPY functions
	•	or design the follow-on detection notebook that builds from this