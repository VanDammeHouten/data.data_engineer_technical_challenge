# BioScout's 2024 Data Engineer Technical Challenge

Welcome to our technical challenge for the data engineering role at BioScout, you have been given a small subset of the
type of data we work with and some analogous problems to solve that we deal with in our data pipelines.

## Your Tasks

### Installation

You have been given an installable python package called `bioscout-tech-challenge` which is built using `poetry`.

Run the following to install the package (assuming you have poetry available as a package on your python interpreter):

```shell
poetry install
```

You can then run the following to see the cli (built using the `cli` module) in action:

```shell
bioscout-tech-challenge hello
```
---------------------------------------------------------------------------------------------------------------------

### Introduction & Submission Instructions

We're asking you for a mixture of data processing, data analysis, and machine learning model evaluation tasks. We're 
looking for your ability to add features to an existing python library as well as your data exploration skills. Feel 
free to add features to the package so that they're accessible via the cli or are helpful modules and methods for use
in your jupyter notebook (or equivalent tool of choice) exploration of the data we've provided.

Be creative with the tools and solution to the problems, this is the time to show off your skills and show the diversity
and excellence of your engineering talents. Do what you think is best and be willing to back your ideas in the follow-up
discussion of your solution, we're excited to discuss your design choices and why you have solved the problems the way
you have.

Please write your solutions as additions / features to the `bioscout-tech-challenge` package, to the standard that 
you'd be happy to put up a PR for review. Any additional writing or analysis is welcomed, please note where to find this
work for each task so that it can be reviewed in your submission

*Note there is a `cli` module already written for you and a bounding box class already created for you within the 
`models` module. We're expecting you to expand upon the `bioscout-tech-challenge` software package and implement a 
design that helps you solve the problems we've put in front of you. We're expecting a working solution to all these 
problems, please make sure your solution runs and is easily re-executable, i.e. dependencies are managed, the cli is
easy to use etc.*

#### How to Submit

Please create a GitHub repository and invite [BioScoutNick](https://github.com/BioScoutNick) so that we can see your
work. We're keen to see a healthy changelog and sensible checkpoints of progress, in order to keep your repo small,
don't worry about committing the original data files we've given you unless you've done some feature engineering or
modifications that necessitate adding them to the repo.


### 1. Pre-Process Weather Data

We've got some weather data in from our new weather system, but it's not easy to query the data, flatten the structure
so that each observation has its own row and every attribute is in its own column. Join the weather observations onto
the device data so that each weather reading has the associated device metadata attached to it. Provide descriptions of
the new data columns and deduce the purpose and origin of this new data.

Save this data somewhere sensible and note in this readme where it can be found so it can be reviewed in your submission

### 2. Visualise Weather Data & Provide Insights

Now that you've pre-processed this weather data into something usable, visualise the various sensors and their data over
time, explain any insights or interesting observations you have about the data. What would you conclude from how the 
sensors are behaving out in the field? 

Write up your analysis and note in this readme where to find what you've written so that it can be evaluated for 
submission.

### 3. Explore Imagery & Bounding Boxes

There are a bunch of images, and a bunch of bounding boxes for a new disease we want to deliver for customers. 
There are some human, and some machine made bounding boxes are provided, there are a couple of tasks to complete here:
 - Suggest & compute performance metrics for the model, 
 - Suggest a confidence threshold cutoff we should use to maximise these metrics.
 - Show areas where the model has made mistakes + explain what has happened.
 - Advise on how you might solve the mistakes the model is making and what we should do to improve the model in the 
    future
 - How could we improve our annotations etc.?

The human annotations are stored as absolute x_min,x_max, y_min, y_max values, and the machine made predictions are 
stored as normalised middle x, middle y values, and normalised width and height values relative to the size of the 
image; the model also has confidence scores attached, these are represented as a float between 0 and 1 for low and high
confidence respectively.

Normalised middle x and middle y values mean that the x & y floats represent the middle of the box relative to the size
of the image, so a middle x value of 0.5 means the center of the bounding box is in the dead center of the image, and a
normalised width of 0.5 means the width of the bounding box is half the width of the image, you can apply the same
logic for the y and height values etc.

## What We're Looking For

Here is how we will evaluate your response, we are looking for the following

- Efficient Problem-Solving
  - We need to solve novel problems and an ability to scope and shape what the crux of an issue is, as well as apply the
    correct solution. This is at the heart of being a great engineer. We want to see that, with re-usability in mind, we like
    to solve problems once and rely on the foundations of yesterday. Being comfortable adding capabilities to the 
    library we've provided and using them within your exploratory jupyter notebook for exploration is a good example of
    applying the right tool for the right job and code re-use.

- Solid Software Engineering Principles
  - We ship and maintain what we write. We're looking for characteristics of code you'd be happy to revisit in the 
    future and rely on while you sleep. We are scaling up, and we are looking for engineers who write robust software.
  - In particular, we're looking for foundational skill-sets such as:
    - Automated Testing
    - Version Control Comfortability
    - Good Software Design
    - Clear Documentation & Easy to Follow Logic
    - Knowledge of Python & Available Packages
  - Don't go overboard on trying to prove out every one of these principles, we can discuss your knowledge of these
    within the final interview, but it certainly doesn't hurt to show off what you know. Having some automated tests
    proving your submission is correct will always score brownie points for example so don't stop yourself from showing
    great work.

- Creativity
  - Show off interesting ideas or questions you can think of with the data we've given you, whether that be interesting 
    correlations or different ways to visualise what we've provided. Even the kinds of models or forecasting you'd like
    to do if you had more data. We have fascinating data at BioScout that requires a creative mind to explore and mine.
    We do world first research on the data we capture. BioScout is an exciting place when you're energised by the 
    'what if' and you're thinking of what is possible in the future with the incredible data we have. We'll be looking
    for pontification of fascinating insights you can either extract from what we've given you or you have thought of
    could be possible with some data augmentation from other sources.
  - If you have your favourite libraries or tools you think solve these problems or could enhance what we've presented
    here we're keen to see them, show off your favourite tools.

- Data Engineering/Science Skills
  - Data Communication
    - Our data is fundamentally novel and exciting. A big responsibility in the data team is to effectively communicate 
      your findings and insights to a broader audience, both internal and external to the company. You are often talking
      to very smart but not necessarily data native stakeholders. An ability to distil but not dumb down your knowledge 
      so that its easy to meaningfully understand by a diverse audience is key.
  - Data Engineering
    - Your ability to manipulate, transform, explain, and maintain data is ultimately what decides how good our models
      are and is what limits our ability to analyse and research our datasets. The more efficiently you can engineer our
      data for what we need it for, the better we can solve the problems we want to address.
  - Data Science
    - We have lots of data, and we want to research and mine it for new answers to interesting questions only we can 
      answer. Whilst this is a data engineering role, its important you feel comfortable interrogating your data for 
      issues of quality or inconsistency. These skills happen to be the same as the kind of analysis we'll need to do 
      from a data science perspective.

**If at anytime you have any questions or feel there is any ambiguity in these instructions, and you'd like 
clarification, please feel free to email nick at nicholas@bioscout.com.au who you interviewed with. He'll be happy to
answer any queries you have, there's also no penalty for asking questions, we want you to have all the information you
need, we're looking for quality and clarity.**

    
