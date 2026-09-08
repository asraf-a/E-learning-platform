import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educa.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.cache import cache
from courses.models import Subject, Course, Module, Content, Text, Video

def populate():
    # 1. Remove the course added by user ('Maths')
    maths_courses = Course.objects.filter(slug='maths')
    count = maths_courses.count()
    if count:
        maths_courses.delete()
        print(f"Removed {count} user-added course(s) ('Maths').")

    instructor = User.objects.get(username='instructor')
    student = User.objects.get(username='student')

    # Ensure Subjects exist
    subjects = {
        'programming': Subject.objects.get_or_create(slug='programming', defaults={'title': 'Programming'})[0],
        'mathematics': Subject.objects.get_or_create(slug='mathematics', defaults={'title': 'Mathematics'})[0],
        'physics': Subject.objects.get_or_create(slug='physics', defaults={'title': 'Physics'})[0],
        'music': Subject.objects.get_or_create(slug='music', defaults={'title': 'Music'})[0],
    }

    # Course catalog data
    courses_data = [
        {
            'slug': 'modern-web-dev-django-react',
            'title': 'Modern Web Development with Django & React',
            'subject': subjects['programming'],
            'overview': 'Build scalable full-stack web applications combining Django REST Framework on the backend with modern React on the frontend.',
            'modules': [
                {
                    'title': 'Backend Fundamentals with Django',
                    'description': 'Master models, migrations, class-based views, and database optimization.',
                    'contents': [
                        {
                            'type': 'text',
                            'title': 'Django Architecture & The MTV Pattern',
                            'content': 'Django follows the Model-Template-View (MTV) architectural pattern. Models represent the data layer and business logic, Templates define the user interface presentation layer, and Views act as the controller that handles HTTP requests and coordinates models with templates.'
                        },
                        {
                            'type': 'video',
                            'title': 'Django Project Architecture Walkthrough',
                            'url': 'https://www.youtube.com/watch?v=F5mRW0jo-U4'
                        },
                        {
                            'type': 'text',
                            'title': 'Optimizing Database Queries with select_related & prefetch_related',
                            'content': 'To prevent N+1 query bottlenecks in Django ORM, use select_related for single-valued relationships (ForeignKey, OneToOneField) which performs a SQL JOIN, and prefetch_related for multi-valued relationships (ManyToManyField, reverse ForeignKey).'
                        }
                    ]
                },
                {
                    'title': 'Building Robust REST APIs with DRF',
                    'description': 'Design clean, hyperlinked REST APIs using Django REST Framework, ModelViewSets, and JWT authentication.',
                    'contents': [
                        {
                            'type': 'text',
                            'title': 'Serializers and ModelViewSets',
                            'content': 'Django REST Framework serializers convert complex querysets into JSON format. ModelViewSets provide out-of-the-box support for standard CRUD operations (list, create, retrieve, update, destroy) with minimal boilerplate.'
                        },
                        {
                            'type': 'text',
                            'title': 'Custom Permissions and Object-Level Security',
                            'content': 'Implement custom BasePermission classes with has_permission and has_object_permission to ensure users only access resources they are authorized to view or edit.'
                        }
                    ]
                },
                {
                    'title': 'Frontend SPA with React & Vite',
                    'description': 'Create an interactive frontend communicating with the Django backend.',
                    'contents': [
                        {
                            'type': 'text',
                            'title': 'React Hooks and State Management',
                            'content': 'Leverage useState, useEffect, and custom hooks to manage component state and asynchronous data fetching from Django REST endpoints.'
                        }
                    ]
                },
                {
                    'title': 'Real-Time WebSockets with Django Channels',
                    'description': 'Add real-time interactivity, chat rooms, and push notifications with Daphne and Channels.',
                    'contents': [
                        {
                            'type': 'text',
                            'title': 'Asynchronous Consumers & Channel Layers',
                            'content': 'Django Channels extends Django to handle asynchronous protocols like WebSockets using ASGI. AsyncWebsocketConsumer provides non-blocking message routing through channel layers backed by Redis or in-memory layers.'
                        }
                    ]
                }
            ]
        },
        {
            'slug': 'calculus-linear-algebra-cs',
            'title': 'Calculus & Linear Algebra for Computer Science',
            'subject': subjects['mathematics'],
            'overview': 'Explore the core mathematical foundations behind computer graphics, machine learning algorithms, and scientific computing.',
            'modules': [
                {
                    'title': 'Vectors and Matrix Operations',
                    'description': 'Understand vector spaces, dot products, cross products, and matrix transformations.',
                    'contents': [
                        {
                            'type': 'text',
                            'title': 'Geometric Interpretation of Vectors & Matrices',
                            'content': 'Matrices can be understood as linear transformations of coordinate space. Multiplying a vector by a matrix translates, rotates, or shears the vector space while keeping grid lines parallel and evenly spaced.'
                        },
                        {
                            'type': 'video',
                            'title': 'Essence of Linear Algebra',
                            'url': 'https://www.youtube.com/watch?v=fNk_zzaMoSs'
                        },
                        {
                            'type': 'text',
                            'title': 'Dot Products and Cosine Similarity',
                            'content': 'The dot product measures the directional alignment between two vectors. In machine learning and NLP, cosine similarity derived from dot products is used extensively for vector search and recommendation embeddings.'
                        }
                    ]
                },
                {
                    'title': 'Differential Calculus & Gradient Descent',
                    'description': 'Derivatives, partial derivatives, the chain rule, and optimization.',
                    'contents': [
                        {
                            'type': 'text',
                            'title': 'The Gradient Vector & Loss Optimization',
                            'content': 'The gradient vector points in the direction of steepest ascent on a multivariable loss surface. By moving in the opposite direction (-grad f), gradient descent iteratively minimizes error in neural networks and optimization models.'
                        }
                    ]
                },
                {
                    'title': 'Eigenvalues, Eigenvectors & PCA',
                    'description': 'Dimensionality reduction, spectral decomposition, and principal component analysis.',
                    'contents': [
                        {
                            'type': 'text',
                            'title': 'Principal Component Analysis (PCA)',
                            'content': 'Eigenvectors identify the axes of maximum variance in high-dimensional data sets. PCA projects data onto these principal axes to reduce dimensionality while preserving maximum informational variance.'
                        }
                    ]
                }
            ]
        },
        {
            'slug': 'classical-mechanics-modern-physics',
            'title': 'Classical Mechanics & Modern Physics',
            'subject': subjects['physics'],
            'overview': 'From Newton laws of motion and electromagnetic fields to quantum mechanics and relativity.',
            'modules': [
                {
                    'title': 'Newtonian Dynamics & Conservation Laws',
                    'description': 'Kinematics, forces, work, kinetic energy, and momentum conservation.',
                    'contents': [
                        {
                            'type': 'text',
                            'title': 'Conservation of Mechanical Energy',
                            'content': 'In a closed system with only conservative forces acting, the sum of kinetic energy (0.5 * m * v^2) and potential energy (m * g * h) remains constant throughout motion.'
                        },
                        {
                            'type': 'video',
                            'title': 'Physics Mechanics Principles',
                            'url': 'https://www.youtube.com/watch?v=b1t41Q3xRM8'
                        }
                    ]
                },
                {
                    'title': 'Electromagnetism & Circuit Physics',
                    'description': 'Coulomb law, Gauss law, magnetic induction, and Maxwell equations.',
                    'contents': [
                        {
                            'type': 'text',
                            'title': 'Maxwell Equations and Wave Propagation',
                            'content': 'James Clerk Maxwell unified electricity and magnetism into four fundamental equations, demonstrating that changing magnetic fields induce electric fields and electromagnetic waves propagate through vacuum at the speed of light.'
                        }
                    ]
                },
                {
                    'title': 'Introduction to Quantum Foundations',
                    'description': 'Photoelectric effect, wave-particle duality, and the Schrödinger equation.',
                    'contents': [
                        {
                            'type': 'text',
                            'title': 'Wave-Particle Duality and Photons',
                            'content': 'Light exhibits both wave-like characteristics (interference, diffraction) and particle-like characteristics (photoelectric emission of electrons). Quantum theory reconciles these observations through wavefunctions.'
                        }
                    ]
                }
            ]
        },
        {
            'slug': 'music-theory-digital-production',
            'title': 'Music Theory & Digital Audio Production',
            'subject': subjects['music'],
            'overview': 'Learn composition, harmonic progressions, digital audio workstations (DAWs), audio synthesis, and mixing.',
            'modules': [
                {
                    'title': 'Scales, Intervals & Harmonic Progressions',
                    'description': 'Major and minor scales, circle of fifths, diatonic triads, and chord voicings.',
                    'contents': [
                        {
                            'type': 'text',
                            'title': 'The Circle of Fifths and Key Signatures',
                            'content': 'The circle of fifths visualizes the geometric relationships among the 12 tones of the chromatic scale, their corresponding key signatures, and associated major and minor keys.'
                        },
                        {
                            'type': 'video',
                            'title': 'Understanding Music Theory in Practice',
                            'url': 'https://www.youtube.com/watch?v=rgaTLrZGlk0'
                        }
                    ]
                },
                {
                    'title': 'Digital Audio Workstations (DAW) & MIDI',
                    'description': 'Arrangement, audio recording, MIDI sequencing, and virtual instruments.',
                    'contents': [
                        {
                            'type': 'text',
                            'title': 'Audio Sampling Rate & Bit Depth',
                            'content': 'According to the Nyquist-Shannon sampling theorem, accurately capturing frequencies up to 20 kHz requires a sampling rate of at least 44.1 kHz. Higher bit depths (24-bit) expand dynamic range and lower the quantization noise floor.'
                        }
                    ]
                },
                {
                    'title': 'Mixing, Equalization & Mastering',
                    'description': 'Frequency shaping, dynamic range compression, stereo widening, and loudness standards.',
                    'contents': [
                        {
                            'type': 'text',
                            'title': 'Dynamic Range Compression & EQ Sculpting',
                            'content': 'Parametric equalizers cut unwanted resonance to carve sonic space for individual instruments. Compressors control transient peaks to deliver a cohesive, punchy master complying with modern streaming LUFS standards.'
                        }
                    ]
                }
            ]
        }
    ]

    for c_data in courses_data:
        course, created = Course.objects.get_or_create(
            slug=c_data['slug'],
            defaults={
                'owner': instructor,
                'subject': c_data['subject'],
                'title': c_data['title'],
                'overview': c_data['overview'],
            }
        )
        if not created:
            course.title = c_data['title']
            course.overview = c_data['overview']
            course.subject = c_data['subject']
            course.save()

        # Enroll student in all courses so they can immediately test & chat
        course.students.add(student)

        # Populate modules
        for mod_idx, m_data in enumerate(c_data['modules']):
            module, m_created = Module.objects.get_or_create(
                course=course,
                title=m_data['title'],
                defaults={
                    'description': m_data['description'],
                    'order': mod_idx
                }
            )
            if not m_created:
                module.description = m_data['description']
                module.order = mod_idx
                module.save()

            # Contents
            for c_idx, item_data in enumerate(m_data['contents']):
                if item_data['type'] == 'text':
                    text_obj, _ = Text.objects.get_or_create(
                        owner=instructor,
                        title=item_data['title'],
                        defaults={'content': item_data['content']}
                    )
                    # Check if already linked
                    from django.contrib.contenttypes.models import ContentType
                    ct = ContentType.objects.get_for_model(Text)
                    if not Content.objects.filter(module=module, content_type=ct, object_id=text_obj.id).exists():
                        Content.objects.create(module=module, item=text_obj, order=c_idx)
                elif item_data['type'] == 'video':
                    video_obj, _ = Video.objects.get_or_create(
                        owner=instructor,
                        title=item_data['title'],
                        defaults={'url': item_data['url']}
                    )
                    from django.contrib.contenttypes.models import ContentType
                    ct = ContentType.objects.get_for_model(Video)
                    if not Content.objects.filter(module=module, content_type=ct, object_id=video_obj.id).exists():
                        Content.objects.create(module=module, item=video_obj, order=c_idx)

        print(f"Course ready: '{course.title}' with {course.modules.count()} modules.")

    # Clear Django cache to ensure catalog and views update immediately
    cache.clear()
    print("Cleared cache.")

if __name__ == '__main__':
    populate()
