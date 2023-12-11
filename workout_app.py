import customtkinter as ctk
from customtkinter import (CTkCanvas as Canvas, 
                           CTkButton as Button, 
                           CTkLabel as Label, 
                           CTkEntry as Entry, 
                           CTkScrollableFrame as ScrollableFrame, 
                           CTkComboBox as ComboBox)

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

import copy
import dill
from datetime import datetime
from PIL import Image

exercises = {}
workouts = {}

try:
    with open("./data/exercises.pkl", "rb") as file:
        exercises = dill.load(file)
    with open("./data/workouts.pkl", "rb") as file:
        workouts = dill.load(file)
except EOFError:
    pass


class Exercise():


    def __init__(self, name, muscles):
        self.name = name
        self.muscles = muscles
        self.log = []
        exercises[self.name] = self


class Workout():


    def __init__(self, name):
        self.name = name
        workouts[self.name] = self
        self.ex_list = {}


    def add_exercise(self, ex_name, sets, reps, weight, set_time, rest_time):
        ex = copy.copy(exercises[ex_name])
        ex.sets = int(sets)
        ex.reps = int(reps)
        ex.weight = int(weight)
        ex.set_time = int(set_time)
        ex.rest_time = int(rest_time)
        self.ex_list[ex_name] = ex


class Menu:


    def __init__(self):
        self.schedule_id = "after"
        self.root = ctk.CTk()
        self.root.grid_anchor("n")        
        ctk.set_window_scaling(1)
        self.home_page()
        self.root.mainloop()


    def home_page(self, back_command=None, *args):
        self.root.after_cancel(self.schedule_id)
        [widget.destroy() for widget in self.root.grid_slaves()]
        c = Canvas(self.root, bg="#242424")
        Button(c, text="Exercises", command=self.ex_page).grid(row=0, column=0)
        Button(c, text="Workouts", command=self.wk_page).grid(row=0, column=1)
        Button(c, text="Exercise Logs", command=self.logs_page).grid(row=0, column=3)
        if back_command:
            self.img_button(c, "./icons/back_icon", lambda:back_command(*args), 28, 28, 0, 4)
        c.grid(pady=(0, 25))


    def inputbox(self, message):
        Label(self.root, text=message).grid()
        entry = Entry(self.root)
        entry.grid()
        return entry


    def update_entry(self, label_text, entry_text, update_command, *args):
        c = Canvas(self.root, bg="#242424", highlightbackground="#242424")
        c.grid()
        Label(c, text=label_text+"  ").grid(row=0, pady=(0, 10))
        entry = Entry(c, textvariable=ctk.StringVar(c, value=entry_text))
        entry.bind("<Return>", command=lambda x:update_command(entry.get(), *args))
        entry.grid(row=0, column=2, pady=(0, 10))
        
    
    def update_ex(self, new, ex_name, category, wk_name=""):
        if ex_name == new: return
        
        ex_list = exercises
        if wk_name:
            ex_list = workouts[wk_name].ex_list
            
        try:
            new = int(new)
            exec(f"ex_list[ex_name].{category} = {new}")
        except ValueError:
            exec(f"ex_list[ex_name].{category} = '{new}'")
            
        if category == "name":
            ex_list[new] = ex_list[ex_name]
            del ex_list[ex_name]
        
        if wk_name:   
            with open("./data/workouts.pkl", "wb") as file:
                dill.dump(workouts, file)
            self.wk_ex_info_page(new if category == "name" else ex_name, wk_name)
        else:
            with open("./data/exercises.pkl", "wb") as file:
                dill.dump(exercises, file)
            self.ex_info_page(new if category == "name" else ex_name)
            

    def img_button(self, master, img_path, command, width, height, row=None, column=None, sticky=None, padx=0):
        icon = ctk.CTkImage(Image.open(img_path+".png"))
        icon_active = ctk.CTkImage(Image.open(img_path+"_active.png"))
        
        button = Button(master, text="", width=width, height=height, command=command, image=icon)
        button.bind("<Enter>", lambda x:button.configure(image=icon_active))
        button.bind("<Leave>", lambda x:button.configure(image=icon))
        button.grid(row=row, column=column, sticky=sticky, padx=padx)


    def buttonbox(self, iterable, info_command, creation_command=None, deletion_command=None, *args, filter="", prev_box=None, play_command=None): 
        if prev_box:
            box = prev_box
            [i.destroy() for i in box.grid_slaves() if type(i) != Entry]
        else:
            box = ScrollableFrame(self.root)
            box.grid()
            
            searchbar = Entry(box, width=200)
            searchbar.bind("<KeyRelease>", command=lambda x:self.buttonbox(iterable, info_command, creation_command, deletion_command, *args, filter=searchbar.get(), prev_box=box))
            searchbar.grid(column=0, sticky="w")
        
        iterable = [i for i in iterable if filter in i.name]
        
        for i,v in enumerate(iterable):
            if deletion_command:
                self.img_button(box, "./icons/deletion_icon", lambda v=v:deletion_command(v.name, *args), 28, 28, i+1, 0, padx=165)
                Button(box, text=v.name, width=165, command=lambda v=v:info_command(v.name, *args)).grid(row=i+1, column=0, sticky="w")
            else:
                Button(box, text=v.name, width=200, command=lambda v=v:info_command(v.name, *args)).grid(row=i+1, column=0, sticky="w")

        if creation_command:
            self.img_button(box, "./icons/creation_icon", lambda:creation_command(*args), 200, 27, column=0, sticky="w")
        
        if play_command:
            self.img_button(box, "./icons/play_icon", lambda:play_command(*args), 200, 28, sticky="w")
        

    def ex_page(self):
        self.home_page()

        Label(self.root, text="Exercise list").grid()
        self.buttonbox(exercises.values(), self.ex_info_page, self.ex_creation_page, self.del_ex)


    def ex_info_page(self, ex_name):
        self.home_page(self.ex_page)

        ex = exercises[ex_name]

        self.update_entry("Name:", ex.name, self.update_ex, ex.name, "name")
        self.update_entry("Muscles:", ex.muscles, self.update_ex, ex.name, "muscles")


    def del_ex(self, ex_name):
        del exercises[ex_name]
        with open("./data/exercises.pkl", "wb") as file:
            dill.dump(exercises, file)
        self.ex_page()


    def ex_creation_page(self):
        self.home_page(self.ex_page)

        name = self.inputbox("Please enter the exercise name")
        muscles = self.inputbox("Please enter the muscles worked")

        Button(self.root, text="Done", command=lambda:self.ex_creation(name.get(), muscles.get())).grid()


    def ex_creation(self, ex_name, ex_muscles):
        if ex_name == "":
            self.ex_creation_page()
            Label(self.root, text="Please do not leave the name box blank").grid()
        else:
            Exercise(ex_name, ex_muscles)
            with open("./data/exercises.pkl", "wb") as file:
                dill.dump(exercises, file)
            self.ex_page()


    def wk_page(self):
        self.home_page()
                
        Label(self.root, text="Workout list").grid()
        self.buttonbox(workouts.values(), self.wk_info_page, self.wk_creation_page, self.del_wk)
        

    def wk_info_page(self, wk_name):
        self.home_page(self.wk_page)

        wk = workouts[wk_name]

        self.update_entry("Workout name:", wk.name, self.update_wk_name, wk.name)
        
        Label(self.root, text="Exercise list").grid()
        self.buttonbox(workouts[wk_name].ex_list.values(), self.wk_ex_info_page, self.wk_ex_creation_page, self.wk_ex_deletion, wk_name, play_command=self.start_wk)        


    def update_wk_name(self, new, wk_name):
        workouts[new] = workouts[wk_name]
        workouts[new].name = new
        del workouts[wk_name]
        with open("./data/workouts.pkl", "wb") as file:
            dill.dump(workouts, file)
        self.wk_info_page(new)


    def wk_ex_info_page(self, ex_name, wk_name):
        self.home_page(self.wk_info_page, wk_name)

        ex = workouts[wk_name].ex_list[ex_name]

        for i in ["name", "muscles", "sets", "reps", "weight", "set_time", "rest_time"]:
            self.update_entry(f"{i.capitalize().replace('_', ' ')}:", eval(f"ex.{i}"), self.update_ex, ex.name, i, wk_name)
          

    def wk_ex_deletion(self, ex_name, wk_name):
        del workouts[wk_name].ex_list[ex_name]
        with open("./data/workouts.pkl", "wb") as file:
            dill.dump(workouts, file)
        self.wk_info_page(wk_name)


    def wk_creation_page(self):
        self.home_page(self.wk_page)

        name = self.inputbox("Please input the workout name")

        Button(self.root, text="Done", command=lambda:self.wk_creation(name.get())).grid()


    def wk_creation(self, wk_name):
        if wk_name == "":
            self.wk_creation_page()
            Label(self.root, text="Please do not leave the box blank").grid()
        else:
            Workout(wk_name)
            with open("./data/workouts.pkl", "wb") as file:
                dill.dump(workouts, file)            
            self.wk_info_page(wk_name)


    def wk_ex_creation_page(self, wk_name):
        self.home_page(self.wk_info_page, wk_name)
                
        Label(self.root, text="Please select the exercise name").grid()
        name = ComboBox(self.root, values=[i for i in exercises.keys() if i not in workouts[wk_name].ex_list.keys()], state="readonly")
        name.grid()

        sets = self.inputbox("Please input the amount of sets")
        reps = self.inputbox("Please input the amount of reps per set (if applicable, otherwise 0)")
        weight = self.inputbox("Please input the amount of weight per rep (if applicable, otherwise 0)")
        set_time = self.inputbox("Please input the amount of time it takes to complete a set in seconds (if applicable, otherwise 0)")
        rest_time = self.inputbox("Please input the amount of rest time between sets in seconds")

        Button(self.root, text="Done", command=lambda:self.wk_ex_creation(wk_name, name.get(), sets.get(), reps.get(), weight.get(), set_time.get(), rest_time.get())).grid()


    def wk_ex_creation(self, wk_name, ex_name, sets, reps, weight, set_time, rest_time):
        try:
            workouts[wk_name].add_exercise(ex_name, sets, reps, weight, set_time, rest_time)
            with open("./data/workouts.pkl", "wb") as file:
                dill.dump(workouts, file)
            self.wk_info_page(wk_name)
        except ValueError:
            self.wk_ex_creation_page(wk_name)
            Label(self.root, text="Do not leave a box blank, and ensure you have entered the correct data type").grid()


    def start_wk(self, wk_name):
        self.home_page(self.wk_info_page, wk_name)

        ex_list = workouts[wk_name].ex_list

        for ex in ex_list.values():
            cur_ex = Label(self.root, text=f"Current exercise: {ex.name}")
            cur_ex.grid()

            weight = Label(self.root, text=f"Weight: {ex.weight}")
            weight.grid()

            for set in range(ex.sets):
                cur_set = Label(self.root, text=f"Current set: {set+1}/{ex.sets}")
                cur_set.grid()

                self.show_timer("Start set", "Set time remaining: ", ex.set_time)
                self.show_timer("Start rest", "Rest time remaining: ", ex.rest_time)
                exercises[ex.name].log.append([datetime.now(), ex.reps, ex.weight, ex.set_time, ex.rest_time])
                with open("./data/exercises.pkl", "wb") as file:
                    dill.dump(exercises, file)
                cur_set.destroy()

            cur_ex.destroy()
            weight.destroy()


    def show_timer(self, button_msg, timer_msg, duration):
        b = Button(self.root, text=button_msg, command=lambda:b.destroy())
        b.grid()
        self.root.wait_window(b)
        for second in range(duration):
            timer = Label(self.root, text=f"{timer_msg} {duration-second}")
            timer.grid()

            var = ctk.IntVar(self.root)
            self.schedule_id = self.root.after(1000, var.set, 1)
            self.root.wait_variable(var)

            timer.destroy()


    def del_wk(self, wk_name):
        del workouts[wk_name]
        with open("./data/workouts.pkl", "wb") as file:
            dill.dump(workouts, file)
        self.wk_page()


    def logs_page(self):
        self.home_page()

        Label(self.root, text="Exercise log list").grid()
        self.buttonbox(exercises.values(), self.ex_log_page)
        
    
    def ex_log_page(self, ex_name):
        self.home_page(self.logs_page)
        logs = exercises[ex_name].log
        categories = ["Reps", "Weight", "Set time", "Rest time"]
        
        # Have drop-down box for reps, weight, set time, rest time
        box = ComboBox(self.root,
                              values=categories, 
                              command=lambda x:self.plot(self.root), 
                              state="readonly")
        box.grid()

        # datetime, reps, weight, set time, rest time
        # Custom graph (choose x and y)
        # When button is clicked, show graph of progress
        # When button is clicked again, hide graph
        # Have it be zoomable and allow hovering on the points to see exact values
        
        
    def on_pick(self, event, master):
        artist = event.artist
        x, y = artist.get_xdata(), artist.get_ydata()
        ind = event.ind
        coordinates = Label(master, text=f'Data point: {x[ind[0]]} {y[ind[0]]}')
        coordinates.grid()

    def plot(self, master):
        fig = Figure(figsize = (5, 5), dpi = 100) 
        test = Canvas(self.root)    
        y = [i**2 for i in range(101)]
        fig.canvas.callbacks.connect("pick_event", lambda x:self.on_pick(x, master))
        plot1 = fig.add_subplot(111)
        plot1.plot(y, marker="o", picker=10)
        
        canvas = FigureCanvasTkAgg(fig,master = master)
        canvas.draw()
        canvas.get_tk_widget().grid()
        toolbar = NavigationToolbar2Tk(canvas,test)
        toolbar.update()
        canvas.get_tk_widget().grid()
        test.grid()


Menu()

# Allow for multiple of the same exercise in a workout
# Add logging (dill, multiple graphs)
# Have notes and a description that is shown for workouts/exercises
# Make the notes editable
# Check similar apps
# Have a beta phase (r/bwf, discord, etc.)
# Launch on ios/google play
# Integrate it into my own version of habitica
