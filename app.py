from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd 
from db_funcs import *
from PIL import Image
import plotly.express as px
from model import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# *******************************************
# App Components
# *******************************************

def update_edited_rows(edited_rows_indices, new_rows, deleted_rows, edited_df, result_df):
	
	for i in deleted_rows:
		result_df = result_df.drop(deleted_rows)

	to_edit_df = result_df.loc[edited_rows_indices]
	for i in edited_rows_indices:
		for col in edited_df.columns:
			if to_edit_df.loc[i,col] != edited_df.loc[i,col]:
				# st.write(to_edit_df.loc[i,col])
				# st.write(edited_df.loc[i,col])
				to_edit_df.loc[i,col] = edited_df.loc[i,col]
				# st.write(to_edit_df.loc[i,col])
				if col == 'task_status':
				
					if edited_df.loc[i,col] == 'In-Progress':
						to_edit_df.loc[i,'start_time'] = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
					
					if edited_df.loc[i,col] == 'Done':
						to_edit_df.loc[i,'end_time']=datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
						# st.write(to_edit_df.loc[i,'end_time'])
						# st.write(edited_df.loc[i,'deadline_date'])
						if edited_df.loc[i,'deadline_date'] < date.today():
							to_edit_df.loc[i,'is_late'] = True 
						else: to_edit_df.loc[i,'is_late'] = False

		
	return to_edit_df


def check_edited_row(edited_row, original_row):
	# st.write(edited_row)
	# st.write(original_row)
	return not edited_row.equals(original_row)

def get_edited_row(edited_df, original_df):
	edited_indices = edited_df.index
	edited_indices_list = list(edited_indices)

	original_indices = original_df.index
	original_indices_list = list(original_indices)	

	edited_rows = []
	new_rows = []
	deleted_rows = []

	for i in original_indices:
		if i not in edited_indices:
			deleted_rows.append(i)

	for i in edited_indices_list:
		if i not in original_indices_list:
			new_rows.append(i)

		if check_edited_row(edited_df.loc[i],original_df.loc[i]):
			edited_rows.append(i)

	return edited_rows, new_rows, deleted_rows

def disable_mood():
	st.session_state['feeling_select']=True

def disable_slider():
	st.session_state['sleep_slider']=True 

def disable_radio():
	st.session_state['medicine_radio']=True 


def color_df(val):
	if val == "Done":
		color = "green"
	elif val == "In-Progress":
		color = "orange"
	else:
		color = "red"  

	return f'background-color: {color}'

st.set_page_config(
    page_title="ToDo Tune",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

top_image = Image.open('static/user.jpeg')
st.sidebar.image(top_image,use_column_width='auto')


# Initialization state
if "avg_mood_int" not in st.session_state:
    st.session_state['avg_mood_int'] = 0
	
if "avg_sleep_hours_int" not in st.session_state:
    st.session_state['avg_sleep_hours_int'] = 0.0

if "medication_taken" not in st.session_state:
    st.session_state['medication_taken'] = False

if 'feeling_select' not in st.session_state:
    st.session_state['feeling_select'] = False

if 'sleep_slider' not in st.session_state:
    st.session_state['sleep_slider'] = False

if 'medicine_radio' not in st.session_state:
    st.session_state['medicine_radio'] = False

if 'res' not in st.session_state:
    st.session_state['res'] = None


st.image('TO DO Tune.svg',)

with st.sidebar:
	choice = option_menu("Menu", ["🎯 My Day","✅ Create Task","🖊️ Edit Tasks", "📝 Recent Tasks"], 
									  icons=[' ', ' ',' ', ' '], menu_icon=' ', default_index=0,
									  styles={
        "container": {"background-color": "#fafafa"},
		"nav-link": {"text-align": "left", "margin":"0px", "--hover-color": "#eee", "font-weight": "normal"},
        "nav-link-selected": {"background-color": "#d0d0d0"}
    })

create_table()

if choice == "🎯 My Day":
	st.subheader("🎯 My Day")

	col_large1,col_large2,col_large3 = st.columns(3,gap='large')
	
	with col_large1:

		feeling_html = """
			<div style="font-size: 85%; padding-bottom:5px;">
				How do you feel today?
			</div>
			"""
		st.markdown(feeling_html, unsafe_allow_html=True)

		col1,col2,col3,col4,col5 = st.columns(5,gap='small')
		with col1:
			if st.button('😁', key='feeling5', on_click=disable_mood, disabled=st.session_state['feeling_select']): #super happy
				st.session_state['avg_mood_int']=5

		with col2:
			if st.button('🙂', key='feeling4', on_click=disable_mood, disabled=st.session_state['feeling_select']): #happy
				st.session_state['avg_mood_int']=4

		with col3:
			if st.button('😐', key='feeling3', on_click=disable_mood, disabled=st.session_state['feeling_select']): #neutral
				st.session_state['avg_mood_int']=3

		with col4:
			if st.button('🙁', key='feeling2', on_click=disable_mood, disabled=st.session_state['feeling_select']): #sad
				st.session_state['avg_mood_int']=2

		with col5:
			if st.button('😭', key='feeling1', on_click=disable_mood, disabled=st.session_state['feeling_select']): #super sad
				st.session_state['avg_mood_int']=1


	with col_large2:
		st.session_state['avg_sleep_hours_int'] = st.slider('How many hours did you sleep at night?', 0.0, 24.0, step=0.25, key='my_slider', on_change=disable_slider, value=st.session_state['avg_sleep_hours_int'], disabled=st.session_state['sleep_slider'])
		st.write(st.session_state['avg_sleep_hours_int'], ' hours.')

	with col_large3:
		res = st.radio('Do you took medicine today?',['Yes', 'No'], index=st.session_state['res'], key='my_radio', on_change=disable_radio, disabled=st.session_state['medicine_radio'])
		if res=='Yes':
			st.session_state['medication_taken'] = True
			st.session_state['res'] = 0
		if res=='No':
			st.session_state['medication_taken'] = False
			st.session_state['res'] = 1

	tab1, tab2, tab3 = st.tabs(["Today's Tasks 📝", "   Analysis   ", "   🔔   "])

	with tab1:
		st.text('Do now and live peacefully:')
		# result = view_all_data()
		# result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'is_late', 'today_date', 'avg_mood_int', 'avg_sleep_hours_int', 'medication_taken'])
		# result_df['deadline_date']=pd.to_datetime(result_df['deadline_date'])
		# clean_df1= result_df[['title', 'tag', 'about', 'task_status', 'deadline_date']]
		# clean_df1['deadline_date'] = result_df['deadline_date'].dt.strftime('%m/%d/%Y')
		# clean_df1 = clean_df1[(clean_df1['deadline_date']==date.today().strftime('%m/%d/%Y'))]
		# st.dataframe(clean_df1.style.applymap(color_df,subset=['task_status']))

		result = get_today_tasks(date.today().strftime('%m/%d/%Y'))
		result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'is_late', 'today_date', 'avg_mood_int', 'avg_sleep_hours_int', 'medication_taken'])
		clean_df1= result_df[['title', 'tag', 'about', 'task_status', 'deadline_date']]
		st.dataframe(clean_df1.style.applymap(color_df,subset=['task_status']))
		
	with tab2:
		st.subheader("Tasks Status Tracker")
		
		result = view_all_data()
		result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'is_late', 'today_date', 'avg_mood_int', 'avg_sleep_hours_int', 'medication_taken'])
		
		done_tasks = result_df[(result_df['task_status']=='Done')]
		done_tasks['deadline_date']=pd.to_datetime(done_tasks['deadline_date']) 
		done_tasks['end_time']=pd.to_datetime(done_tasks['end_time'])
		done_tasks = done_tasks[['title','tag','deadline_date','end_time','is_late']]
		done_tasks['is_late'] = done_tasks['is_late'].astype('int64')

		late_done_tasks = done_tasks[(done_tasks['is_late']==1)]
		on_time_done_tasks = done_tasks[(done_tasks['is_late']==0)]

		
		one_month_later = date.today() + relativedelta(months=2)

		fig = make_subplots(rows=1, cols=2)

		trace0 = go.Histogram(x=late_done_tasks['deadline_date'], 
							name='Lated Tasks',
							xbins=dict(
							end=str(one_month_later),
							size= 'M1'), # 1 months
							autobinx = False
							)
		# trace1 = go.Histogram(x=x, nbinsx = 8)
		trace1 = go.Histogram(x=on_time_done_tasks['deadline_date'],
							name='On-Time Tasks',
							xbins=dict(
							end=str(one_month_later),
							size= 'M1'), # 1 months
							autobinx = False
							)

		fig.append_trace(trace0, 1, 1)
		fig.append_trace(trace1, 1, 2)

		fig.update_layout(title = {"text": "Completed Tasks Distribution Over The Time","x": 0.3, })

		st.plotly_chart(fig,use_container_width=True)

		# late_done_tasks['deadline_month'] = late_done_tasks['deadline_date'].dt.month
		# late_done_tasks['end_month'] = late_done_tasks['end_time'].dt.month
		# late_done_tasks['deadline_year'] = late_done_tasks['deadline_date'].dt.year

		# on_time_done_tasks['deadline_month'] = on_time_done_tasks['deadline_date'].dt.month
		# on_time_done_tasks['end_month'] = on_time_done_tasks['end_time'].dt.month
		# on_time_done_tasks['deadline_year'] = on_time_done_tasks['deadline_date'].dt.year

		# on_time_done_tasks_gb = on_time_done_tasks.groupby(['deadline_year','deadline_month']).size()
		# late_done_tasks_gb = late_done_tasks.groupby(['deadline_year','deadline_month']).size()

		# monthly_late_tasks = late_done_tasks_gb.reset_index()
		# monthly_on_time_tasks = on_time_done_tasks_gb.reset_index()
  
	with tab3:
		st.subheader("What to do next?")
		model_result = run_ml_model()

		title = model_result['title'].values[0]
		# title = str(title)
		tag = model_result['tag'].values[0]
		# tag = str(tag)

		st.text('It seems you are considering delaying the "' + title + '"  task under the "' + tag + '" category!')


if choice == "✅ Create Task":
	st.subheader("Add New Task")

	col1,col2 = st.columns(2)

	with col1:
		title = st.text_input("Title")
		about = st.text_area("Description")
		
	with col2:
		tag = st.selectbox("Category",["home", "bureaucracy", "studies", "work", "exercise", "fun", "health"])
		deadline_date = st.date_input("Due Date")
		deadline_date = deadline_date.strftime('%m/%d/%Y')
		deadline = deadline_date + ' 11:59:59 PM'
		time_estimation = st.number_input(label="Estimated Time (hours)", min_value=0,)
		task_status = st.selectbox("Status",["To-Do","In-Progress"])

	if task_status == "In-Progress":
			start_time=datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
	else: start_time=None

	if task_status == "Done":
			end_time=datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
			if deadline < end_time:
				is_late = True 
			else: is_late = False
	else:
		end_time=None
		is_late = None

	if st.button("Add Task"):
		today_date = date.today().strftime('%m/%d/%Y')
		avg_sleep_hours_int = st.session_state['avg_sleep_hours_int']
		avg_mood_int = st.session_state['avg_mood_int']
		medication_taken = st.session_state['medication_taken']
		add_row(title, tag, deadline, deadline_date, about, task_status, time_estimation, start_time, end_time, is_late, today_date, avg_mood_int, avg_sleep_hours_int, medication_taken)
		# st.success("Added Task \"{}\" ✅".format(title))
		# st.balloons()
		st.toast("Added Task \"{}\" ✅".format(title))




elif choice == "🖊️ Edit Tasks":
	st.subheader("Update Items")

	result = view_all_data()
	result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'is_late', 'today_date', 'avg_mood_int', 'avg_sleep_hours_int', 'medication_taken'])
	result_df['deadline_date'] = pd.to_datetime(result_df['deadline_date'])
	result_df['deadline_date'] = result_df['deadline_date'].dt.date

	# with st.expander("View Data"):
	# 	st.dataframe(result_df.style.applymap(color_df,subset=['task_status']))

	original_df = result_df[['title', 'tag', 'deadline_date', 'about', 'task_status']]
	# original_df['deadline_date'] = pd.to_datetime(original_df['deadline_date'])
	# original_df['deadline_date'] = original_df['deadline_date'].dt.date
	# original_df['deadline_date'] = original_df['deadline_date'].dt.strftime('%m/%d/%Y')
	original_df = original_df[(original_df['task_status'] != 'Done')]
	# original_df = original_df.style.applymap(color_df,subset=['task_status'])
	edited_df = st.data_editor(original_df, hide_index=True, use_container_width=True, num_rows="dynamic",
							column_config={
								'tag' : st.column_config.SelectboxColumn(
									"tag",
									options=["home", "bureaucracy", "studies", "work", "exercise", "fun", "health"],
									required=True,
								),
								'task_status' : st.column_config.SelectboxColumn(
									"task_status",
									options=["To-Do","In-Progress","Done"],
									required=True,
								),
								'deadline_date' : st.column_config.DateColumn(
									"deadline_date",
									min_value=date(1900, 1, 1),
									max_value=date(2005, 1, 1),
									step=1,
								),
							},)
	
	# edited_df.compare(original_df)
	# st.dataframe(edited_df)
	# st.dataframe(original_df)

	edited_rows_indices, new_rows, deleted_rows = get_edited_row(edited_df, original_df)

	# st.write(deleted_rows)

	if original_df.shape[0]!=edited_df.shape[0]:
		for i in deleted_rows:
			guid = result_df.loc[i]['guid']
			# st.write(guid)
			delete_row_by_guid(int(guid))



	original_df = original_df.drop(deleted_rows)
	# st.dataframe(original_df)
	diff_df = edited_df.compare(original_df)

	if (not diff_df.empty):
		# st.dataframe(diff_df)

		edited_df['deadline_date'] = pd.to_datetime(edited_df['deadline_date'])
		edited_df['deadline_date'] = edited_df['deadline_date'].dt.date
		# edited_df['deadline_date'] = edited_df['deadline_date'].dt.strftime('%m/%d/%Y')

		# st.dataframe(edited_df)
		# st.dataframe(original_df)

		# edited_rows_indices, new_rows, deleted_rows = get_edited_row(edited_df, original_df)

		edited_result_df = update_edited_rows(edited_rows_indices, new_rows, deleted_rows, edited_df, result_df)
		# edited_result_df['deadline_date'] = pd.to_datetime(edited_result_df['deadline_date'])
		# edited_result_df['deadline_date'] = edited_result_df['deadline_date'].dt.date
		# st.dataframe(edited_result_df)
		
		# st.dataframe(edited_result_df)

		if not edited_result_df.empty:
			for i in edited_rows_indices:
				guid = result_df.loc[i]['guid']
				delete_row_by_guid(int(guid))
			
			# st.dataframe(edited_result_df)
			for i in edited_rows_indices:
				title = edited_result_df.loc[i]['title']
				tag = edited_result_df.loc[i]['tag']
				deadline = edited_result_df.loc[i]['deadline']
				deadline_date = edited_result_df.loc[i]['deadline_date']
				deadline_date = deadline_date.strftime('%m/%d/%Y')
				about = edited_result_df.loc[i]['about']
				task_status = edited_result_df.loc[i]['task_status']
				time_estimation = edited_result_df.loc[i]['time_estimation']
				start_time = edited_result_df.loc[i]['start_time']
				end_time = edited_result_df.loc[i]['end_time']
				is_late = edited_result_df.loc[i]['is_late']
				today_date = edited_result_df.loc[i]['today_date']
				avg_mood_int = edited_result_df.loc[i]['avg_mood_int']
				avg_sleep_hours_int = edited_result_df.loc[i]['avg_sleep_hours_int']
				medication_taken = edited_result_df.loc[i]['medication_taken']
				# st.write(type(avg_mood_int),type(avg_sleep_hours_int),type(medication_taken))

				# st.write(title, tag, deadline, deadline_date, about, task_status, time_estimation, start_time, end_time, is_late, today_date, int(avg_mood_int), float(avg_sleep_hours_int), bool(medication_taken))

				add_row(title, tag, deadline, deadline_date, about, task_status, time_estimation, start_time, end_time, is_late, today_date, int(avg_mood_int), float(avg_sleep_hours_int), bool(medication_taken))

		# result = view_all_data()
		# result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'is_late', 'today_date', 'avg_mood_int', 'avg_sleep_hours_int', 'medication_taken'])
		# st.dataframe(result_df)

	# st.dataframe(edited_df)






	# list_of_tasks = [i[0] for i in view_all_task_names()]
	# selected_task = st.selectbox("Task",list_of_tasks)
	# task_result = get_task(selected_task)

	# if task_result:
	# 	task = task_result[0][0]
	# 	task_status = task_result[0][1]
	# 	task_due_date = task_result[0][2]

	# 	col1,col2 = st.columns(2)

	# 	with col1:
	# 		new_task = st.text_area("Task To Do",task)

	# 	with col2:
	# 		new_task_status = st.selectbox(task_status,["To-Do","In-Progress","Done"])
	# 		new_task_due_date = st.date_input(task_due_date)

	# 	if st.button("Update"):
	# 		edit_task_data(new_task,new_task_status,new_task_due_date,task,task_status,task_due_date)
	# 		st.success("Updated Task \"{}\" ✅".format(task,new_task))

	# 	with st.expander("View Updated Data 💫"):
	# 		result = view_all_data()
	# 		clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
	# 		st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))




# elif choice == "❌ Delete Task":
# 	st.subheader("Delete")
# 	with st.expander("View Data"):
# 		result = view_all_data()
# 		result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'is_late', 'today_date', 'avg_mood_int', 'avg_sleep_hours_int', 'medication_taken'])
# 		st.dataframe(result_df.style.applymap(color_df,subset=['task_status']))

# 	unique_list = [i[0] for i in view_all_task_names()]
# 	delete_by_task_name =  st.selectbox("Select Task",unique_list)
# 	if st.button("Delete ❌"):
# 		delete_data(delete_by_task_name)
# 		st.warning("Deleted Task \"{}\" ✅".format(delete_by_task_name))

# 	with st.expander("View Updated Data 💫"):
# 		result = view_all_data()
# 		clean_df = pd.DataFrame(result,columns=["Task","Status","Date"])
# 		st.dataframe(clean_df.style.applymap(color_df,subset=['Status']))




elif choice == "📝 Recent Tasks":
	st.subheader("Don't let time tick away this month! Dive into your tasks now.")
	result = view_all_data()
	result_df = pd.DataFrame(result,columns=['guid', 'title', 'tag', 'deadline', 'deadline_date', 'about', 'task_status', 'time_estimation', 'start_time', 'end_time', 'is_late', 'today_date', 'avg_mood_int', 'avg_sleep_hours_int', 'medication_taken'])
	
	# clean_df= result_df[['title', 'task_status', 'deadline_date']] 
	# task_df = clean_df['task_status'].value_counts().to_frame()
	# task_df = task_df.reset_index()

	col1,col2 = st.columns(2)
	with col1:
		clean_df = result_df[['title', 'tag', 'task_status', 'deadline_date']]
		clean_df['deadline_date'] = pd.to_datetime(clean_df['deadline_date'])
		clean_df = clean_df[((clean_df['deadline_date'].dt.month == datetime.now().month) & (clean_df['deadline_date'].dt.year == datetime.now().year)) | (clean_df['task_status'] != 'Done')]
		
		task_df = clean_df['task_status'].value_counts().to_frame()
		task_df = task_df.reset_index()

		task_df.rename(columns={"index": "Status", "task_status": "Count"}, inplace=True)
		
		st.dataframe(clean_df.style.applymap(color_df,subset=['task_status']))	
	
	with col2:
		p1 = px.pie(task_df,names='Status',values='Count', color='Status', color_discrete_map={'To-Do':'red', 'Done':'green', 'In-Progress':'orange'})
		st.plotly_chart(p1,use_container_width=True)

	# clean_df1 = result_df[['title', 'tag', 'task_status', 'deadline_date']]
	# clean_df1['deadline_date'] = pd.to_datetime(clean_df1['deadline_date'])
	# clean_df1 = clean_df1[((clean_df1['deadline_date'].dt.month == datetime.now().month) & (clean_df1['deadline_date'].dt.year == datetime.now().year)) | (clean_df1['task_status'] != 'Done')]
	# st.dataframe(clean_df1.style.applymap(color_df,subset=['task_status']))	

	with st.expander("View All 📝"):
		clean_df1 = result_df[['title', 'tag', 'task_status', 'deadline_date']]
		clean_df1['deadline_date'] = pd.to_datetime(clean_df1['deadline_date'])
		st.dataframe(clean_df1.style.applymap(color_df,subset=['task_status']))

