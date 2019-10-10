# Django-shop
DJANGO-Shop

Se da lista de produse. Fiecare utilizator isi poate crea mai multe liste cu preferinte de produse (wishlists)
Fiecare utilizator poate adauga un produs in unul din listele cu preferinte
Pentru fiecare produs din lista, trebuie sa fie aratat cati utilizatori unici, au dorit acest produs (adaugat in wish list).

Pretul produselor de obicei este dictat de situatia din piata.
Si avem nevoie de un instrument, care ne va permite sa monitorizam pretul de comercializare a produselor, pentru fiecare zi in parte.

Utilizatorul poate adauga un produs in magazinul sau.
Fiecare produs are un pret de comercializare.
Utilizatorul poate modifica pretul de comercializare din ziua curenta pentru o perioada nedefinita.
Utilizatorul la fel poate modifica pretul pentru un interval de timp (o zi sau mai multe) din trecut, de cate ori doreste.

Trebuie returnat pretul pentru un anumit produs pentru o anumita perioada pe fiecare zi.

Istoricul modificarilor trebuie pastrat. Produsele sunt grupate in categorii de produse, si utilizatorul poate modifica atat pretul pentru toata categoria, cat si pentru un item aparte, conform conditiilor anterioare.