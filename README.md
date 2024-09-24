# Social Network Web App

This repository contains the code for a social network web application, designed to enable users to interact through threads, follow other users, and contribute with posts and comments. Built with Django and Bootstrap, this app focuses on simplicity, user engagement, and content recommendation based on user activity.

## Features

- **User Registration & Authentication**: Users can register, log in, and securely access the platform using password encryption.
- **Threads & Posts**: Users can create threads, participate in discussions, and engage with content by adding posts and comments.
- **Voting System**: A voting system (+1, -1) allows users to express their opinion on posts.
- **Following & Feed**: Users can follow other users, and the feed will display posts from followed users and subscribed threads.
- **Content Recommendation**: The app includes a recommendation engine that suggests threads and users based on the user's activity.
- **User Moderation**: Administrators have the power to ban users from creating content and manage the community.

## Technologies Used

- **Backend**: Django
- **Frontend**: Bootstrap, HTML
- **Database**: SQLite3
- **Other Libraries**:
  - **NumPy**: Used for calculating user similarity in the recommendation system.
  - **Pillow**: Image processing for thread cover images.
  - **Django-crispy-forms**: Simplifies form rendering.
