// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility that Flutter provides. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/testing.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:http/http.dart' as http;
import 'package:winning_streak/multiple_choice_question/fetcher/question_fetch.dart';
import 'package:winning_streak/multiple_choice_question/fetcher/random_question_fetch.dart';
import 'package:winning_streak/multiple_choice_question/mc_question.dart';

// Real class
class Cat {
  String sound() => "Meow";
  bool eatFood(String food, {bool? hungry}) => true;
  Future<void> chew() async => print("Chewing...");
  int walk(List<String> places) => 7;
  void sleep() {}
  void hunt(String place, String prey) {}
  int lives = 9;
}
// Fake class
class FakeCat extends Fake implements Cat {
  @override
  bool eatFood(String food, {bool? hungry}) {
    print('Fake eat $food');
    return true;
  }
}

void main() {
  test("cat example", () async {

    var cat = FakeCat();
    cat.eatFood("cake");
    cat.sleep();
  });


  //Fetcher that fetches a valid json
  Future<String> jsonFromFile(String filePath) async {
    final file = File(filePath);
    String rawJson = await file.readAsString();
    return rawJson;
  }

  RandomQuestionFetch getFetcher(String filePath) {
    return RandomQuestionFetch(
        client:MockClient((request) async {
          String rawJSON = await jsonFromFile(filePath);
          return http.Response(
              rawJSON,
              200,
              headers: {'content-type': 'application/json'});
        })
    );
  }


  group('sanity checks', ()
  {
    late QuestionFetch fetcher;

    setUp( ()  {
      fetcher = getFetcher("test_resources/valid.json");
    });

    test("fetcher returns a MCQuestion object", () {
      expect(fetcher.fetch(), completion(isA<MCQuestion>()));
    });

    test("category with \" \" is parsed correctly", () async {
      MCQuestion mcQuestion = await fetcher.fetch();
      expect(mcQuestion.category,"\"cat\" egory");
    });

    test("4 choices parsed from valid category", () async {
      MCQuestion mcQuestion = await fetcher.fetch();
      expect(mcQuestion.choiceCount,4);
    });

    test("question text exists", () async {
      MCQuestion mcQuestion = await fetcher.fetch();
      expect(mcQuestion.questionText,isA<String>());
    });

    test("question text is one of", () async {
      MCQuestion mcQuestion = await fetcher.fetch();

      List<String> options = [
        "Malcolm McDowell & Nastassja Kinski's \"purr\"fect roles in 1982",
      ];


      //expect(mcQuestion.questionText,isA<String>());
    });

  });
}
