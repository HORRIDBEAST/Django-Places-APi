import os
import django
import random
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reviews.models import User, Place, Review

fake = Faker()

PLACE_TYPES = [
    'Restaurant', 'Cafe', 'Coffee Shop', 'Doctor', 'Dentist',
    'Grocery Store', 'Pharmacy', 'Gym', 'Salon', 'Spa',
    'Bar', 'Bakery', 'Bookstore', 'Electronics Store', 'Clothing Store'
]

REVIEW_TEXTS = {
    5: [
        "Absolutely amazing! Exceeded all my expectations.",
        "Outstanding service and quality. Highly recommend!",
        "Perfect experience from start to finish.",
        "Best in the area, hands down. Will definitely return!",
        "Exceptional quality and friendly staff. Five stars!"
    ],
    4: [
        "Very good overall, would visit again.",
        "Great experience with minor room for improvement.",
        "Solid choice, I'm satisfied with my visit.",
        "Good quality and service, worth checking out.",
        "Pleasant experience, will likely return."
    ],
    3: [
        "Decent but nothing special.",
        "Average experience, met basic expectations.",
        "It's okay, could be better in some areas.",
        "Fair quality for the price.",
        "Acceptable but has room for improvement."
    ],
    2: [
        "Disappointing, expected more.",
        "Below average experience, not impressed.",
        "Had some issues that need to be addressed.",
        "Wouldn't recommend based on my experience.",
        "Service was lacking, not great overall."
    ],
    1: [
        "Terrible experience, would not return.",
        "Very poor service and quality.",
        "Extremely disappointed, avoid if possible.",
        "Worst experience I've had, not recommended.",
        "Awful service, complete waste of time."
    ]
}


def populate_database():
    print("Starting data population...")
    
    print("\nClearing existing data...")
    Review.objects.all().delete()
    Place.objects.all().delete()
    User.objects.all().delete()
    
    print("Creating users...")
    users = []
    for i in range(50):
        phone = f"+1{random.randint(2000000000, 9999999999)}"
        name = fake.name()
        try:
            user = User.objects.create_user(
                phone_number=phone,
                name=name,
                password='password123'
            )
            users.append(user)
            if (i + 1) % 10 == 0:
                print(f"  Created {i + 1} users...")
        except Exception as e:
            print(f"  Error creating user: {e}")
            continue
    
    print(f"Created {len(users)} users")
    
    print("\nCreating places...")
    places = []
    for i in range(100):
        place_type = random.choice(PLACE_TYPES)
        name = f"{fake.company()} {place_type}"
        address = fake.address().replace('\n', ', ')
        try:
            place = Place.objects.create(
                name=name,
                address=address
            )
            places.append(place)
            if (i + 1) % 20 == 0:
                print(f"  Created {i + 1} places...")
        except Exception as e:
            print(f"  Error creating place: {e}")
            continue
    
    print(f"Created {len(places)} places")
    
    print("\nCreating reviews...")
    reviews_created = 0
    for place in places:
        num_reviews = random.randint(0, 10)
        reviewed_users = random.sample(users, min(num_reviews, len(users)))
        
        for user in reviewed_users:
            rating = random.choices(
                [1, 2, 3, 4, 5],
                weights=[5, 10, 20, 35, 30],
                k=1
            )[0]
            
            text = random.choice(REVIEW_TEXTS[rating])
            
            try:
                Review.objects.create(
                    user=user,
                    place=place,
                    rating=rating,
                    text=text
                )
                reviews_created += 1
            except Exception as e:
                print(f"  Error creating review: {e}")
                continue
        
        if (reviews_created) % 50 == 0:
            print(f"  Created {reviews_created} reviews...")
    
    print(f"Created {reviews_created} reviews")
    
    print("\n" + "="*50)
    print("Data population completed!")
    print("="*50)
    print(f"Total Users: {User.objects.count()}")
    print(f"Total Places: {Place.objects.count()}")
    print(f"Total Reviews: {Review.objects.count()}")
    print("\nSample login credentials:")
    sample_user = User.objects.first()
    if sample_user:
        print(f"  Phone: {sample_user.phone_number}")
        print(f"  Password: password123")


if __name__ == '__main__':
    populate_database()