SPICE_CONTEXT = """
# About SPICE (SIT–Polytechnic Innovation Centre of Excellence)

**SPICE**, launched 1 March 2022, is a national innovation platform under the **Singapore Institute of Technology (SIT)**, supported by **Enterprise Singapore**.  It partners with polytechnic **Centres of Innovation (COIs)** and SIT’s **Applied Research Centres (ARCs)** to give SMEs and industry players rapid access to:

- **Domain Experts & Technical Teams**  
- **Specialized Facilities & Equipment**  
- **Interdisciplinary Talent** (students, faculty, POs)  
- **Shared Risk & Co-development Frameworks**

---

## Mission & Value to Industry

SPICE helps companies:

1. **Scope & Define** problem statements  
2. **Ideate** innovative concepts together  
3. **Co-create** prototypes, products, services  
4. **Validate & Scale** toward commercialization  

By reducing upfront investment and de-risking R&D, SPICE accelerates industry innovation.

---

## Capabilities at a Glance

| Domain                                  | Key Services & Tools                                                              |
|-----------------------------------------|-----------------------------------------------------------------------------------|
| **Autonomous Systems & Robotics**       | ROS, motion planning, tele-operation, sensor fusion, mechanical design            |
| **Electronics & Control Systems**       | IoT/Industrial IoT, embedded firmware, PCB/circuit design, PLC/SCADA/HMI          |
| **Software & AI**                       | ML/DL, NLP/LLMs, generative AI, computer vision, full-stack & mobile apps         |
| **Data Analytics & Visualization**      | EDA, predictive/prescriptive analytics, interactive dashboards (Plotly, Power BI) |
| **Food Technology & Processing**        | Formulation, sensory testing, process optimization, 3D food printing              |
| **Mechanical System Design**            | CAD, rapid prototyping (3D print), powertrain design, CNC process workflows       |
| **Medical & Therapy Systems**           | Medical device prototyping, bio-instrumentation, regulatory guidance              |
| **Testing & Inspection**                | ICP-OES/MS, GC-MS, TGA/DSC, XRD, AFM/FESEM, NDT (ultrasonic, X-ray)                |
| **Cybersecurity & Communications**      | 5G integration, secure IoT, OT security frameworks                                |
| **Augmented & Virtual Reality**         | AR/VR prototyping, human-machine interfaces                                       |

---

## Collaboration Network

### At SIT ARCs
- CITE, CTIL, DF@SIT, EETC, FoodPlant, FCTLab, RaPID Centre

### At Polytechnic COIs
- Aquaculture Innovation Centre (AIC)  
- Complementary Health Product COI (COI-CHP)

---

**Usage**  
Use this context to ground the model in SPICE’s mission, process, and multi-domain expertise before asking it to:
- Identify partnership opportunities  
- Draft outreach emails  
- Map business entities  
- Propose technical solutions  
"""


robotics_context = """
# AUTONOMOUS SYSTEMS & ROBOTICS

### Robot Software and Intelligence

- Robot software and intelligence are built on key components such as robotics middleware, motion planning, and human-robot interaction. Frameworks like the Robot Operating System (ROS) enable modular control and communication across robotic systems. Advanced motion planning and manipulation algorithms allow robots to operate efficiently in dynamic environments. At the same time, software-driven human-robot interfaces and telemanipulation systems ensure intuitive and responsive interaction between humans and machines.

### Robot Mechanical Design and Embodiment
 
- Designing mechanical components, actuators, and structural frameworks that support the robot’s intended tasks, ensuring strength, precision, and adaptability in real-world environments.
 
### Robot Perception and Integration
 
- Designing and interfacing custom sensors and electronics to enable accurate sensing and environmental awareness. This includes integrating hardware and software components to process sensor data effectively, forming the foundation for intelligent decision-making and adaptive robot behavior.
 
### Human-Robot Interaction and Control
 
- Designing telemanipulation systems and feedback mechanisms that allow users to interact with and control robots effectively, ensuring smooth, safe, and responsive collaboration.
 
# Examples
 
### Autonomous Delivery Drone
 
- This project focuses on designing and developing an autonomous drone capable of delivering small packages. It integrates navigation systems, obstacle detection, and path planning algorithms to allow the drone to fly safely and efficiently from a warehouse to a designated drop-off location, reducing human involvement in the delivery process.
 
### Autonomous Warehouse Robot
 
- This project involves designing a robot that can navigate a warehouse, picking up and transporting goods autonomously. The robot uses computer vision for object recognition, sensors for navigation, and AI for decision-making. The goal is to reduce labor costs and improve inventory management in warehouses
"""


electronic_context = """
# ELECTRONIC, ELECTRICAL & CONTROL SYSTEM

### Internet-of-Things Solutions

- We design and implement IoT solutions that connect devices, sensors, and systems for real-time data collection, remote monitoring, and intelligent decision-making. Our capabilities include edge computing, cloud integration, and custom dashboards to optimize operations and enable predictive insights.

### Embedded System Design

- We specialize in developing custom embedded systems using microcontrollers, SoCs, and real-time operating systems. Our solutions are optimized for reliability, low power consumption, and performance, supporting applications in automation, control, and smart devices.

### Circuit and PCB Design

- From concept to prototype, we provide complete circuit design and PCB layout services. Our team ensures signal integrity, EMC compliance, and manufacturability, delivering robust designs tailored for industrial, consumer, or custom electronics applications.

### Control System Design

- We design and implement precise and reliable control systems for industrial and process automation. This includes PLC, SCADA, and HMI programming, PID tuning, motion control, and safety systems to ensure efficient and stable operation of machines and processes.
"""

software_context = """
# SOFTWARE ENGINEERING/ PROGRAMMING

### AI, Machine Learning, Generative AI and Computer Vision

We harness the power of AI to build intelligent systems that learn, adapt, and innovate. From
traditional machine learning models to cutting-edge generative AI and computer vision solutions, our
capabilities drive automation, personalization, and smarter outcomes. Our expertise includes:
- Supervised and unsupervised machine learning
- Natural language processing (NLP) and large language models (LLMs)
- Generative AI (text, image, and code generation)
- Computer vision (object detection, image classification, video analytics)
 
### Data Analytics and Visualisation

We transform raw data into meaningful insights through advanced analytics and compelling visual
storytelling. From exploratory data analysis to interactive dashboards, our team empowers decisionmakers
with clarity and confidence. We specialize in:
- Data cleaning and wrangling
- Descriptive and predictive analytics
- Interactive dashboards using tools like Plotly, Tableau, and Power BI
- Custom data visualizations for web and mobile platforms
 
### Software and Application Development (Web, Mobile, Full-Stack)
 
We design and build robust, scalable, and user-centric software applications across platforms. Our
team combines strong engineering practices with modern UI/UX design to deliver seamless digital
experiences. We offer:
- Custom web application development (frontend & backend)
- Mobile app development (iOS, Android, cross-platform)
- Full-stack solutions using modern frameworks (e.g., React, Node.js, Python, .NET)
- API development and integration
- Agile development, DevOps, and continuous delivery pipelines
 
### Embedded Software Development

- We develop intelligent embedded systems and IoT solutions that connect the physical and digital worlds. Our team integrates hardware, firmware, and cloud technologies to enable real-time monitoring, automation, and control across diverse environments

#Examples

### Deep Learning-based Machine Vision for Defect Detection

- Design and implementation of deep learning-powered computer vision systems for automated product inspection. Capable of detecting manufacturing defects with high accuracy, enabling real-time quality control and reducing manual inspection efforts.

### Generative AI for Career Coaching Chatbot

- Development of intelligent career coaching chatbot using generative AI, large language models (LLMs), and retrieval-augmented generation (RAG). Supports personalised guidance by understanding user goals, retrieving relevant information, and providing contextual, human-like advice.
"""

food_technology_context = """
# FOOD TECHNOLOGY

### Product Formulation

- The process of designing and optimizing food recipes by selecting and combining ingredients to achieve desired taste, texture, nutrition, shelf life, and cost-effectiveness. It ensures the product meets consumer preferences, regulatory standards, and quality requirements.

### Product Characterisation

- Involves analyzing and identifying the physical, chemical, sensory, and functional properties of a food product. This process ensures quality, consistency, and compliance with standards while supporting product development and optimization.

### Process Optimisation

- The improvement of manufacturing processes to enhance efficiency, product quality, and cost-effectiveness. It involves refining techniques, reducing waste, and ensuring consistency while maintaining safety and compliance with standards.

### Food Innovation

- The development of new or improved food products, processes, or technologies to meet changing consumer demands, enhance nutrition, sustainability, and convenience, and drive industry growth.

# Examples:

### Food Waste Upcycling

- Transforming food industry by-products or waste (e.g., fruit peels, coffee grounds) into edible products, animal feed, or bio-based materials.

### 3D Food Printing

- Using 3D printing technology to create intricate food designs or customized meals, especially for healthcare and dietary needs.

### Food Packaging

- Food packaging techniques include edible packaging made from consumable materials, sustainable packaging using eco-friendly and biodegradable options, and smart packaging with sensors and indicators to monitor freshness and quality.

### Novel Food Processing Technologies

- Ultrasound Processing: Utilizing high-frequency sound waves to enhance food processing techniques such as emulsification, extraction, and microbial inactivation.
"""

mechanical_context = """
# MECHANICAL SYSTEM DESIGN

### Mechanical System Development

- With core strengths in Mechanical System Development, the team excels in power drive selection, mechanical component integration, and process-based system design—ensuring optimized performance and reliability. For instance, in the industrial automation design, the group efficiently selected servo drives and gear systems to balance precision and torque.
 
### Manufacturing Process Development

- In Manufacturing Process Development, the team translates designs into scalable, cost-effective manufacturing strategies, such as streamlining CNC machining workflows for custom housings or designing jigs for automated assembly lines.

### CAD to 3D-Printing Rapid Prototyping

- 3D-Printing Rapid Prototyping capability drastically reduces development cycles by enabling quick, iterative testing of mechanical assemblies—for example, producing functional prototypes of gearing system and cam driven system within days. This integrated approach ensures faster product validation, reduced time-to-market, and robust mechanical solutions tailored to customer needs.
 
# Examples:

### Automated Assembly Line Machine

- This project focuses on designing a mechanical system for an automated assembly line, which could include robotic arms, conveyors, and sorting mechanisms. The system will reduce production time and human error by automating repetitive tasks, ensuring high precision and efficiency in mass production environments

### Wind Turbine Mechanical System Design

- This project aims to develop a mechanical system for a wind turbine that converts wind energy into electricity. The system would include rotor blades, gearbox, and generator mechanisms, with a focus on efficiency, durability, and minimizing wear and tear from harsh environmental conditions.
"""

testing_context = """
# TESTING & INSPECTION

### Chemical Analysis

- We provide elemental and molecular characterization through techniques such as ICP-OES, (upcoming) ICP-MS, LC-MS, GC-MS, FTIR, and UV-Vis. These methods enable the detection of trace metals, identification of organic compounds, and functional group analysis for applications across materials, environmental, pharmaceutical, and food sectors.

### Physical Analysis

- Our physical testing capabilities include thermal analysis (TGA, DSC), morphological characterization (AFM, FESEM, particle size analysis), crystallinity and thin film assessment (XRD). These tools support comprehensive evaluation of material behavior, structure, and performance.

### Biological Analysis

- We support cell culture, synthetic biology, and bioprocess monitoring, enabling assays involving microbial or mammalian cells. These capabilities are used for evaluating biological activity, optimizing culture conditions, and supporting research in biologically derived products.

### Food Analysis

- Our food analysis capabilities include rheological and texture analysis, as well as ingredient analysis such as proximate analysis, protein content, and hydrocolloid characterization. We also offer sensory evaluation and shelf-life studies to support product development and stability.

# Examples:

### Noble Metal Recovery Analysis from Spent Catalysts

- In this project, the goal is to analyze spent catalysts for their noble metal content, such as platinum, palladium, and rhodium. The project involves developing reliable sample preparation and digestion protocols, followed by instrumental analysis (e.g., ICP-OES) to quantify metal concentrations. The objective is to support resource recovery, waste valorization, and process optimization by accurately determining the residual value of noble metals in deactivated industrial catalysts.

### Non-Destructive Testing for Aerospace Components

- This project involves using non-destructive testing (NDT) methods, such as ultrasonic or X-ray testing, to inspect the integrity of aerospace components. The goal is to identify any defects or material weaknesses that could compromise safety without damaging the parts, ensuring compliance with strict industry standards.
"""


SPECIALIZED_CONTEXTS = {
    "Robotics": robotics_context,
    "Electronics": electronic_context,
    "Software": software_context,
    "FoodTechnology": food_technology_context,
    "Mechanical": mechanical_context,
    "Testing": testing_context,
}
