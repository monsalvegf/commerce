from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    # Django crea automáticamente un campo de clave primaria (id) que se autoincrementa

    # Nombre de la categoría
    name = models.CharField(max_length=100)

    # Descripción de la categoría
    description = models.TextField(blank=True)

    # Métodos adicionales
    def __str__(self):
        return self.name

class Listing(models.Model):
    # Django crea automáticamente un campo de clave primaria (id) que se autoincrementa

    # Relación con el usuario que crea el listado (tu modelo User personalizado)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")

    # Detalles básicos del listado
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True) # Opcional

    # Estado del listado
    is_active = models.BooleanField(default=True)

    # Relación con el modelo Category
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")

    # Fechas de creación y finalización
    created_at = models.DateTimeField(auto_now_add=True)
    ends_at = models.DateTimeField()

    # Métodos adicionales
    def __str__(self):
        return f"{self.title} - {self.starting_bid}"


class Bid(models.Model):
    # Django crea automáticamente un campo de clave primaria (id) que se autoincrementa

    # Relación con el listado
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    # Relación con el usuario que realiza la puja
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

    # Cantidad de la puja
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Fecha y hora de la puja
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} - {self.listing.title} - ${self.amount}"


class Comment(models.Model):
    # Django crea automáticamente un campo de clave primaria (id) que se autoincrementa

    # Relación con el listado
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    # Relación con el usuario que realiza el comentario
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")

    # Contenido del comentario
    content = models.TextField()

    # Fecha y hora del comentario
    comment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter.username} - {self.listing.title} - {self.comment_time}"


class Watchlist(models.Model):
    # Django crea automáticamente un campo de clave primaria (id) que se autoincrementa

    # Relación con el usuario
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")

    # Relación con el listado
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlists")

    class Meta:
        unique_together = ('user', 'listing')  # Evita duplicados en la lista de seguimiento para un usuario y listado específicos.

    def __str__(self):
        return f"{self.user.username}'s watchlist - {self.listing.title}"