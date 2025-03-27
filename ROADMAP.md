
# First steps

Create an easy React Vite Shadcn Site
Create GCC project and get scope credentials 
Build out simple tool calls with GCC + metadata grabbing
build PydanticAI agent flow with tool calls + orchestrator-worker setup (because this task is easily replicable and we can run multiple workers at once)



# BEGIN BRAINSTORMING


# this is a doc with a roadmap/brainstorming space on impproving the app


agnostic to user’s needs - this will be accomplished in tha sample frontend

dropdown on LHS - prompter on bottom left

to tweak the type of image recognition (gemini and Rekognition)

need to have a filebrowser view of Gdrive (and google drive signin as login) - build in infra to whitelist users

option to move the actual file, or to create a copy of the new one

Existing dashboard of certain types of images - live value updating

charts for info - expecially searching by date/type of photo

I want to have a progress bar along with the visualization

**Metadata**

be able to see the location/important metadata - and read image titles to add into context w/ gemini

need to be able to see parent folders and add this structure into context in a relevant way

GCC

Making a sample project

need to authenticate for certain actions (i.e not moving/deleting files)

Maybe THREE modes for different levels of security) - read, read/create, and move

**Security**

Make sure to emphasize existence of tmp/ file creation if necessary

**Agents**

ideating a new way to organize

creating a tag for each image from gemini prompt, and then being able to organize them with RAG and key values from redis? (THIS WOULD BE A POTENTIAL INTERESTING MAJOR CHANGE FROM THE PRIOR WORK)

this would be a good way to build out folder structure - with PydanticAI

gemini function calling with pydantic AI and building concise context based on the job

weigh between pydantic and llamaindex

TOOLS LIST:

 image recognition, create file, move file, copy file, get metadata, get parent folders

Tech stack

Pydantic

Pillow

YAML
Gemini (flash model) with multimodal

Redis

TODO

test pricing differences between the two models (Rekognition + old school gemini interaction)

Fix single-thread processing

Build out web frontend with GUI and way to see the current processes

(ASYNCH)

building CLI into the functionality too

Rip out AWS Rekognition (if pricepoint isn’t way worse)

GCC google login - that is it - with way to READONLY all of drive structure 

see if redis has a place for this

Build out running data analysis window with information on images - connecting this to the redis database