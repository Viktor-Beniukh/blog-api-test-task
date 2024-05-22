# Blog API (test task)

"""
API service for management of a blog written on FastAPI.
"""


### Installing using GitHub

- Python3 must be already installed
- Install PostgreSQL and create db

```shell
git clone https://github.com/Viktor-Beniukh/blog-api-test-task.git
cd blog-api-test-task
python3 -m venv venv
source venv/bin/activate
pip install poetry
poetry install
python main.py 
```

You need to create `.env` file and add there the variables with your according values:
- `POSTGRES_DB`: this is databases name;
- `POSTGRES_USER`: this is username for databases;
- `POSTGRES_PASSWORD`: this is username password for databases;
- `POSTGRES_HOST`: this is host name for databases;
- `POSTGRES_PORT`: this is port for databases;
- `DATABASE_URL=postgresql+driver://user:pass@host:port/dbname`: it's a format of database url
  (for local work - `host` - `localhost` or `127.0.0.1`, into Docker - image name of database)
- `SECRET_KEY` and `JWT_SECRET_KEY`: this is Django Secret Key - by default is set automatically when you create a Django project.
                You can generate a new key, if you want, by following the link: `https://djecrety.ir`;
- `ALGORITHM`: needed to create tokens



## Run with docker

Docker should be installed

- Create docker image: `docker-compose build`
- Run docker app: `docker-compose up` or `docker-compose up -d` (to work in this terminal)



## Getting access

- Create user via /api/auth/register/
- Get access token via /api/auth/login/



## Features

- JWT authentication;
- Documentation is located at /docs;
- Creating category, post, tag, author and profile;
- Reading category, post, tag, author and profile;
- Updating category, post, tag, author profile data;
- Deleting category, post, tag, author profile;


### What do APIs do

- [GET] /api/v1/categories/ - obtains a list of categories (only admin or moderator);
- [GET] /api/v1/posts/ - obtains a list of posts;

- [GET] /api/v1/categories/id/slug/posts - obtains a list of posts for specific category;
- [GET] /api/v1/posts/slug/ - obtains the specific post;

- [POST] /api/v1/categories/ - creates a category (only admin or moderator);
- [POST] /api/v1/posts/ - creates a post (by current user);
- [POST] /api/v1/posts/id/upload-image/ - uploads a post image (by author of the post);
- [POST] /api/v1/posts/id/add_tags/ - creates and adds tags to the post (by author of the post);

- [PUT] /api/v1/categories/id/update/ - updates the category data (only admin or moderator);
- [PUT] /api/v1/tags/id/ - updates the tag data (only admin or moderator);

- [PATCH] /api/v1/posts/id/update/ - partial updates the post data (by author of the post);

- [DELETE] /api/v1/categories/id/delete/ - deletes the category data (only admin or moderator);
- [DELETE] /api/v1/posts/id/delete/ - deletes the post data (by author of the post);
- [DELETE] /api/v1/posts/id/remove_tag/ - deletes the tag from the post (by author of the post);
- [DELETE] /api/v1/tags/id/ - deletes the tag (only admin or moderator);

- [GET] /api/authors/me/ - obtains the specific author information data;
- [GET] /api/authors/me/my_posts/ - obtains a list of posts for current author;
- [GET] /api/authors/id/posts/ - obtains a list of posts for specific author;

- [POST] /api/authors/me/change_password/ - changes the password data for the current author;
- [POST] /api/authors/me/profile/ - creates a profile for the current author;
- [POST] /api/authors/me/upload-image/ - uploads the profile image for the current author;

- [PUT] /api/authors/change_role/ - changes a role of authors (only admin);

- [PATCH] /api/authors/me/profile/ - partial updates the profile of the current author;

- [DELETE] /api/authors/me/profile/ - deletes the profile of the current author;

- [POST] /api/auth/register/ - creates new authors;
- [POST] /api/auth/login/ - creates token pair for author;

- [GET] /api/auth/refresh_token/ - gets new access token for author by refresh token;



### Checking the endpoints functionality
- You can see detailed APIs at swagger page: `http://127.0.0.1:8000/docs/`.
