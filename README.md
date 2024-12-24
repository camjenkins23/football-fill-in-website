# Football Fill-In Website
## Description
The Football Fill-In Website is a dynamic and interactive platofrm for the fans of the Football Fill-In show. This website provides fans with access to a vast archive of videos and an engaging quiz based on the questions taken directly from the show. Designed with simplicity and accessibility in mind, the platform ensures an enhjoyable experience for new and old fans alike.

## Features
### 1. Video Archive
* Access to a complete library of past shows.
* Advanced filtering options to search for videos by title, guest or week. 
### 2. Quiz Section
* Test your knowledge with quizzes generated from the database of show-related questions.
* Randomized questions to ensure a new quiz every time.
### 3. User Friendly Design
* Simple Navigation and responsive layout for easy access across different devices.

## Setup
### Prerequisites
* Python 3.9+
* Flask and required Python packages (see ```requirements.txt```)
### Steps to Run Locally
#### 1. Clone the repository
```bash
git clone https://github.com/camjenkins23/football-fill-in-website.git
cd football-fill-in-website
```
#### 2. Set Up the Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
#### 3. Environment Variables
* Create a .env file in the root directory.
* Replace your ```secret_key_here``` with a secure random key.
```txt
SECRET_KEY=your_secret_key_here
 ```
 #### 4. Run the Application
 * Start a flask development server:
 ```bash
 python run.py
 ```

 ## Project Structure
 ```bash
 football-fill-in/
├── app/
│   ├── __init__.py        
│   ├── routes.py          
│   ├── utils.py           
│   ├── static/            
│   │   └── styles.css
│   ├── templates/         
│       ├── layout.html
│       ├── index.html
│       ├── archive.html
│       ├── quiz.html
│       └── sorry.html
├── instance/
│   └── ffin.example.db    
├── .env                  
├── requirements.txt       
├── run.py                 
├── README.md              
 ```

## Future Enhancements
* ### Forum Functionality:
    * The forum is currently disabled but can be re-enabled by updating the ```routes.py``` file.
* ### Deployment:
    * Hosting the application on a third-party platform for broader accessibility.