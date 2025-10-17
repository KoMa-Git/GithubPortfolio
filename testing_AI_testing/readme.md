# AI is everywhere, I have to learn how to use it in an efficient way. 
This folder contains my experiment testing GitHub Copilot Agent Mode with different models to help me write a library API and tests (finally Postman tests made by me to practice).

I'd like to:
- gain experience in writing good prompts, and find best practices. 
- get a better understanding of AI's differences - where each is better or worse - to get the most of out them.
- test myself in finding root cause of errors and bugs (if they even make errors at all...and yes, they do) after a short period of practicing to code this kind of app.

I just use the free version of Copilot, which doesn't include the newest models. Since newest models are more effective, end results could be slightly different. When i find time i'll check those as well.
But a library API is kind of basic stuff, free AI versions surely find many many references online.

## Let's see what was made
You can find both versions in their folders. I went further with the Claude version and after correcting small things and adjusting the responses to my taste I: 
**deployed it on Render**: https://library-api-7y4z.onrender.com/docs 
**created API tests with Postman**: https://www.postman.com/koma-4884/portfolio

## Prompting approach and how it evolved:
I started with natural language, without any specification on the app's structure or behaviour. My idea was to reach the goal in iterations, adding endpoints and functions later - which might indicate changes in the core structure (like SQL tables, connections). It's a challenge from real life and it was challenging for AI as well, even in this small-scale project. 
Claude and GPT both "sweated" and started to make mistakes. The logic was good, but they left chunks of code unused from earlier versions, since they focused only on the part i asked to change, without checking how those changes would affect the rest of the code. So when it failed to run i gave them error codes, even though i already knew what caused that failure. Sometimes they fixed it, sometimes they started an endless loop adding more and more code without actually changing the broken part.
On the other hand i've learned coding practices, they add nice ideas and solutions.
After these trials, i decided to write a longer [prompt](/testing_AI_testing/prompt.txt) with more detailed specification and better structure which probably won't need to change later.

## Outcomes:
In about 10 seconds both wrote a working API. It was elevating and devastating at once. Why am I learning to code and read documentation if it is that easy?! 
After checking their resulta, a few glitches came up. Both used a deprecated function and the database wouldn't populate with sample data at the start. (I guess they found more reference code online using that function.) Some response formats were weird, defenitely need changes there too. But so far so good. With background knowledge (which is why i need to learn and practice) when you have an idea where to look after getting an error code, it becomes a very powerful tool.

## Differences:
It was interesting to see 2 different approaches by the agents. Even after many clean starts with the same prompt, both kept their original concept:
- **GPT** writes all the code in one file. In a less complex project like this, that might be better. With changes, it has less chance of missing related parts. Probably easier to create tests, fewer integration issues.
- **Claude** splits the code in separate files with meaningful names and keeps related functions grouped. That suits larger projects better, especially when collaborating or splitting tasks. It also helps if the code needs to be extended later and probably makes debugging easier too. However when i asked to create unit, function or e2e tests it failed, couldn't manage the imports correctly.