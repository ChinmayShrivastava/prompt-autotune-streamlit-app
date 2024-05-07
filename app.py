import streamlit as st
from prompt_autotune.TunePrompt import TunePrompt

st.title("Prompt Autotune")

if "task" not in st.session_state or "prompt" not in st.session_state:
	with st.form("tune_prompt_form"):
		st.write("### Enter the task you want to accomplish")
		task = st.text_area("Task")

		st.write("### Enter your initial prompt")
		prompt = st.text_area("Prompt")

		submit_button = st.form_submit_button("Tune Prompt")

		if submit_button:
			st.session_state.task = task
			st.session_state.prompt = prompt
			st.rerun()

if "task" in st.session_state and "prompt" in st.session_state:
	st.write(f"Task: {st.session_state.task}")
	st.write(f"Prompt: {st.session_state.prompt}")

	if "tuner" not in st.session_state:
		with st.spinner("Generating synthetic examples..."):
			st.session_state.tuner = TunePrompt(
				task=st.session_state.task,
				prompt=st.session_state.prompt,
				verbose=False
			)

	if "extracker" not in st.session_state:
		st.session_state.extracker = {
			i.id: False for i in st.session_state.tuner.examples
		}

	if not all(st.session_state.extracker.values()):
		# display one example at a time
		example = next(i for i in st.session_state.tuner.examples if not st.session_state.extracker[i.id])
		with st.form(f"example_{example.id}"):
			st.write(f"### Example {example.id}")
			st.write(f"Input: {example.input}")
			st.write(f"Output: {example.output}")
			feedback = st.selectbox("Use this example?", ["Yes", "No"])
			submit_button = st.form_submit_button("Submit")

			if submit_button:
				example.use = feedback == "Yes"
				st.session_state.extracker[example.id] = True
				st.rerun()

	if all(st.session_state.extracker.values()):

		if "current_cycle" not in st.session_state:
			st.session_state.current_cycle = 0

		if "tuning_complete" not in st.session_state:
			if st.session_state.tuner.number_of_cycles <= st.session_state.current_cycle:
				st.session_state.tuning_complete = True
				st.rerun()
			with st.spinner(f"Running tuning cycle {st.session_state.current_cycle+1}..."):
				st.session_state.tuner.generate_responses_from_prompt(st.session_state.current_cycle)
				st.session_state.tuner.evaluate_responses(st.session_state.current_cycle)
				st.session_state.tuner.tune_prompt(st.session_state.current_cycle)
				st.session_state.current_cycle += 1
			st.rerun()

		if st.session_state.tuning_complete:
			st.write("Tuning complete!")
			st.write(f"Final prompt: {st.session_state.tuner.prompt}")


# if "tune_prompt" not in st.session_state:
# 	st.session_state.tune_prompt = TunePrompt()