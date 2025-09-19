Eg of flow - same as daily recommendations, with the only change being the prompt here is augmented further by the user for a more focused and granular people discovery experience 
The user says: 
“I want to find people interests in AI and physics, and who love to play tennis. I don’t want to see smokers, peoples with tattoos etc..” 
The system returns 5 highest ranked profiles. 

High level overview of the search architecture - for both natural language search and proactive daily recommendations:
In the initial phase, phase, before we cross 5k users, our curation system would follow this architecture 
Loop A
When a search is initiated - either natural language search, or when the user clicks on "Daily recommendations" on the app, the system goes through all profiles (profiles with obvious, high level mismatch are excluded from the search - in terms of distance (only consider profiles geolocation n miles within the user's location, n set by the user, in terms of gender, in other things like diet, smoking, lifestyle, etc - we could set these as hard filters later on to reduce the search work done by our LLM)
Loop B
As it goes through each of the remaining relevant profile, it assigns each a multidimensional compatibility score, a total score, some remarks and feedback. At the end of this loop, once it has gone through everyone, it compiles a list of the top 5/n profiles. And displays it to the user. The next day, it shows the next 5, and so on. Until we run out of profiles above the user set threshold ("only show me profiles that are above 90% compatible"), at which point we repeat loop A, but with a deeper user persona model (so better modelling and thus accuracy), and more users (again, same thing).

Past 5k users - building a much more scalable system 
Again, we don't have to consider the entire user base for searches 
In later 1 of this architecture, using hard filters - location and distance, gender, lifestyle, values, etc - we prune out most irrelevant profiles. In phase 2, we do Loop A and Loop B as above. 
Every Sunday/Monday at 5am ET, the system could also do this automatically, to find ever fresher, ever more relevant people.  




