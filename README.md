# LCC Watcher

This app helped me monitor production while being a LCC operator (Local Control Center)


ScreenShots:

Dashboard:
 ![Placeholder Image](https://github.com/peterxie1311/lccwatcher/blob/main/Screenshot%202024-02-26%20at%208.37.08%20pm.png?raw=true)


This shows some of the alers that show up on my dashboard when an action is required from one of the operators in the control room.

Production Calculator
![Placeholder Image](https://github.com/peterxie1311/lccwatcher/blob/main/Screenshot%202024-02-26%20at%208.37.08%20pm.png?raw=true)

This is a calculator to see: 
- How many picks need to be completed before production can stop
- How long it will take before we can stop production and start cleaning 
- The estimated time it will take given we pick at a certain average.



WorkFlows Integration:
![Placeholder Image](https://github.com/peterxie1311/lccwatcher/blob/main/Screenshot%202024-02-26%20at%208.40.05%20pm.png?raw=true)

I've also integrated a feature where it will send the LCC groupchat a string so that the information is easily copy and pastable to have a more efficient work flow.

Descriptions:

This app parses an email using google API's and downloads the latest export data sent from a system in order to alert actions required.

Instructions to run:

For now I haven't inculded an environment version of this but it will be shortly updated.

In the meantime please install all of the packages required to for this applications to run in the imports file. then just click compile on test.py



