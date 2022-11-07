Docker desktop is required to be running for the program to work.

To run the program, navigate to the folder directory in terminal.

Run the command:

docker-compose build

Once the images build, run the following command in terminal:

docker-compose up



Now you should see 3 workers declare themselves, 2 clients request a file and receive it. Any received files
can be seen in the ./endFiles directory. They can be compared with the original files in the 
./worker/files directory.