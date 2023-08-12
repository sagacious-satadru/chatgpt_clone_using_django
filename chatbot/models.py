from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Chat(models.Model): # this would help us have a new data table named Chat in our database
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username} : {self.message}"
