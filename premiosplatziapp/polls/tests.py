from audioop import reverse
import datetime
from operator import index 

from django.test import TestCase
from django.urls.base import reverse
from django.utils import timezone

from .models import Question

# Create your tests here.
# Models and Views

class QuestionModelTest(TestCase):

    def test_was_published_recently_with_future_questions(self):
        """was_published_recently returns False for question whose pub_date is in the future"""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(question_text="¿Quien es el mejor Course Director de Platzi?", pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_past_questions(self):
        """was_published_recently returns False for questions whose pub_date is in the past"""
        time = timezone.now() - datetime.timedelta(days=1.01)
        past_question = Question(question_text="¿Cual es el curso mas complicado en Platzi?", pub_date=time)
        self.assertIs(past_question.was_published_recently(), False)
    
    def test_was_published_recently_with_now_questions(self):
        """was_published_recently returns True for questions whose pub_date is recently created (now)"""
        time = timezone.now()
        now_question= Question(question_text="¿Cual es el curso mas largo de Platzi?", pub_date=time)
        self.assertIs(now_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    create a question with the given "question_text", and published the given
    number of days offset to now (negative for questions piblished in the past,
    positive for questions that have yet to be published))
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """If no question exist, an appropiate message is displayed"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context["latest_question_list"],[])
    
    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on the index page
        """
        create_question("future question", days=30)
        response= self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page
        """
        question= create_question("Past question", days=-10)
        response= self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question])
    
    def test_future_question_and_past_question(self):
        """
        Even if both past and future quetion exist, only past questions are displayed
        """
        past_question = create_question(question_text="Past question", days=-30)
        future_question = create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question]
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions"""
        past_question1 = create_question(question_text="Past question 1", days=-30)
        past_question2 = create_question(question_text="Past question 2", days=-40)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question1, past_question2]
        )


class QuestionDetailViewTests(TestCase):
    
    def test_future_question(self):
        """
        the detail view of a question with a pub_date in the future returns a 404 error - not found 
        """
        future_question = create_question(question_text="Future question", days=30)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """the detail view of a question with pub_date in the past, displays the question's text"""

        past_question = create_question(question_text="FPast question", days=-30)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)