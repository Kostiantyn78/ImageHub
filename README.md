# ImageHub

<p align="center">
  <img src="http://res.cloudinary.com/dyhtnkitj/image/upload/v1709056165/ImageHubProjectDB/user_1/original_images/ttu63ajzijfgp7ydjinm.jpg"
  alt="ImageHub" width="256" height="256">
</p>

---

ImageHub is a REST API application implemented using the FastAPI framework.
It allows users to upload, manage, and share photos, and interact through comments.

---


## Table of Contents

- [Technologies](#technologies)
- [Basic functionality](#basic-functionality)
  - [Authentication](#authentication)
  - [Working with photos](#working-with-photos)
  - [Comments](#comments)
  - [Profile](#profile)
- [Usage](#usage)
  - [Installation](#installation)
  - [Additional information](#additional-information)
- [License](#license)
- [Authors](#authors)

____

## Technologies

| **Module**                                                     | **Description**    |
|----------------------------------------------------------------|--------------------|
| [FastAPI](https://fastapi.tiangolo.com/)                       | Framework          |
| [Pydantic](https://pydantic-docs.helpmanual.io/)               | Validation library |
| [SQLAlchemy](https://docs.sqlalchemy.org/)                     | ORM                |
| [Alembic](https://alembic.sqlalchemy.org/en/latest/)           | Migration tool     |
| [PostgreSQL](https://www.postgresql.org/)                      | Database           |
| [Cloudinary](https://cloudinary.com/)                          | Image hosting      |
| [Passlib](https://passlib.readthedocs.io/en/stable/)           | Password hashing   |
| [Qrcode](https://pypi.org/project/qrcode/)                     | QR code generator  |
| [Pillow](https://pypi.org/project/Pillow/)                     | Image processing   |

____
## Basic functionality

### Authentication

**Endpoints:**

```
POST /api/auth/signup
```
```
POST /api/auth/login
```
```
GET /api/auth/refresh_token
```
```
GET /api/auth/confirmed_email/{token}
```
```
POST /api/auth/request_email
```


The application uses JWT tokens for authentication. Users have three roles: regular user, moderator, and administrator.

To implement different access levels (regular user, moderator, and administrator),
FastAPI decorators are used to check the token and user role.

### Working with photos

**Users can perform various operations related to photos:**

- Upload photos with descriptions.
    ```
    POST /api/images/upload_image
    ```
- Delete photos.
    ```
    DELETE /api/images/{picture_id}
    ```
- Edit photo descriptions.
    ```
    PATCH /api/images/{picture_id}
    ```
- Retrieve a photo by a unique link.
    ```
    GET /api/images/{picture_id}
    ```
- Add up to 5 tags per photo.


- Apply basic photo transformations using 
[Cloudinary services](https://cloudinary.com/documentation/image_transformations).
    ```
    POST /api/transform/create_transform/{natural_photo_id}
    ```
- Generate links to transformed images for viewing as URL and QR-code. Links are stored on the server.

With the help of [FastAPI decorators, described above](#authentication), 
administrators can perform all CRUD operations with user photos.

### Comments

**Under each photo, there is a comment section. Users can:**

- Add and read comments to each other's photos.
  ```
  POST /api/comments/{image_id}
  ```
  ```
  GET /api/comments/all/{image_id}
  ```
- Edit comment.
  ```
  PATCH /api/comments/{comment_id}
  ```
- Administrators and moderators [if you have the role](#authentication) can delete comments.
  ```
  DELETE /api/comments/{comment_id}
  ```

### Profile

**Endpoints for user profile:**

- See your profile.
    ```
    GET /api/users/me
    ```
- Change your avatar.
    ```
    PATCH /api/users/avatar
    ```
- See another user's profile.
    ```
    GET /api/users/{username}
    ```

- Create a route for a user profile based on their unique username.
It returns all user information, including name, registration date, and the number of uploaded photos.

____
  
## Usage

### Installation

- Clone the repository.
```Shell
  git clone https://github.com/Kostiantyn78/ImageHub.git
```

- Install dependencies.

*using poetry*
```Shell
  poetry install
```

- Setup the ".env" file.
```Shell
  cp .env.example .env
```
*and fill in the information you need, run the docker container and create the database if use Postgres *

- Run the application.
```Shell
  uvicorn main:app --reload
```

- Enjoy using application via link in the terminal.

____

### Additional information

- [Documentation](http://localhost:63342/ImageHub/docs/_build/html/index.html?_ijt=bievmo05hld2bt65j03j40vh49&_ij_reload=RELOAD_ON_SAVE)
- [Swagger documentation
- ](http://127.0.0.1:8000/docs#)
- [GitHub](https://github.com/Kostiantyn78/ImageHub)

____

## License
This project is distributed under the **MIT** license.
____


## Authors
The **PyCrafters** Team:
- [Yuliia Didenko](https://github.com/yulyan407)
- [Maksim Nesterovskyi](https://github.com/legendarym4x)
- [Kostiantyn Gorishnyi](https://github.com/Kostiantyn78)
- [Taras Barskyi](https://github.com/Barskyi)
____