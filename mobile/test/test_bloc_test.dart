import 'package:flutter_test/flutter_test.dart';
import 'package:skillbridge/domain/entities/career.dart';
import 'package:skillbridge/domain/entities/question.dart';
import 'package:skillbridge/domain/entities/assessment_result.dart';
import 'package:skillbridge/domain/repositories/career_repository.dart';
import 'package:skillbridge/domain/usecases/get_test_questions.dart';
import 'package:skillbridge/domain/usecases/submit_test_answers.dart';
import 'package:skillbridge/presentation/blocs/test/test_bloc.dart';
import 'package:skillbridge/presentation/blocs/test/test_event.dart';
import 'package:skillbridge/presentation/blocs/test/test_state.dart';

class FakeCareerRepository implements CareerRepository {
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class FakeGetTestQuestionsUseCase extends GetTestQuestionsUseCase {
  FakeGetTestQuestionsUseCase(super.repository);

  List<Question> questions = [];
  bool shouldThrow = false;

  @override
  Future<List<Question>> call(List<String> interests, String locale) async {
    if (shouldThrow) throw Exception('API error');
    return questions;
  }
}

class FakeSubmitTestAnswersUseCase extends SubmitTestAnswersUseCase {
  FakeSubmitTestAnswersUseCase(super.repository);

  AssessmentResult? result;
  bool shouldThrow = false;

  @override
  Future<AssessmentResult> call({
    required List<String> interests,
    required Map<String, int> answers,
    required String locale,
  }) async {
    if (shouldThrow) throw Exception('API error');
    if (result == null) throw Exception('No result configured');
    return result!;
  }
}

void main() {
  group('TestBloc Tests', () {
    late FakeGetTestQuestionsUseCase getQuestionsUseCase;
    late FakeSubmitTestAnswersUseCase submitAnswersUseCase;
    late TestBloc bloc;

    final q1 = const Question(
      id: 'q1',
      scenario: 'Scenario 1',
      questionText: 'Question 1',
      options: [
        AnswerOption(id: 'o1', text: 'Option 1', categoryTag: 'technology'),
        AnswerOption(id: 'o2', text: 'Option 2', categoryTag: 'technology'),
      ],
    );

    final q2 = const Question(
      id: 'q2',
      scenario: 'Scenario 2',
      questionText: 'Question 2',
      options: [
        AnswerOption(id: 'o3', text: 'Option 3', categoryTag: 'technology'),
        AnswerOption(id: 'o4', text: 'Option 4', categoryTag: 'technology'),
      ],
    );

    final career = const Career(
      id: 'c1',
      title: 'Software Developer',
      category: 'it',
      emoji: '💻',
      description: 'Writes code',
      matchPercentage: 99,
      skills: ['Flutter'],
      fitReason: 'Great match',
    );

    final assessmentResult = AssessmentResult(
      personalitySummary: 'Great personality',
      strengths: ['Coding'],
      weaknesses: ['Design'],
      recommendedCareers: [career],
    );

    setUp(() {
      final repository = FakeCareerRepository();
      getQuestionsUseCase = FakeGetTestQuestionsUseCase(repository);
      submitAnswersUseCase = FakeSubmitTestAnswersUseCase(repository);
      bloc = TestBloc(
        getQuestionsUseCase: getQuestionsUseCase,
        submitAnswersUseCase: submitAnswersUseCase,
      );
    });

    tearDown(() {
      bloc.close();
    });

    test('initial state is TestInitial', () {
      expect(bloc.state, const TestInitial());
    });

    test('LoadQuestionsEvent loads questions successfully and emits QuestionsLoaded', () async {
      getQuestionsUseCase.questions = [q1, q2];
      bloc.add(const LoadQuestionsEvent(interests: ['it'], locale: 'uz'));

      expectLater(
        bloc.stream,
        emitsInOrder([
          const QuestionsLoading(),
          QuestionsLoaded(
            interests: const ['it'],
            questions: [q1, q2],
            answers: const {},
            currentIndex: 0,
          ),
        ]),
      );
    });

    test('LoadQuestionsEvent empty list emits TestError', () async {
      getQuestionsUseCase.questions = [];
      bloc.add(const LoadQuestionsEvent(interests: ['it'], locale: 'uz'));

      expectLater(
        bloc.stream,
        emitsInOrder([
          const QuestionsLoading(),
          const TestError('error', previousState: TestInitial()),
        ]),
      );
    });

    test('LoadQuestionsEvent error emits TestError', () async {
      getQuestionsUseCase.shouldThrow = true;
      bloc.add(const LoadQuestionsEvent(interests: ['it'], locale: 'uz'));

      expectLater(
        bloc.stream,
        emitsInOrder([
          const QuestionsLoading(),
          const TestError('error', previousState: TestInitial()),
        ]),
      );
    });

    test('SelectAnswerEvent stores answer in state', () async {
      getQuestionsUseCase.questions = [q1, q2];
      bloc.add(const LoadQuestionsEvent(interests: ['it'], locale: 'uz'));
      await bloc.stream.skip(1).first; // Wait until loaded

      bloc.add(const SelectAnswerEvent(questionId: 'q1', score: 5));

      expectLater(
        bloc.stream,
        emits(QuestionsLoaded(
          interests: const ['it'],
          questions: [q1, q2],
          answers: const {'q1': 5},
          currentIndex: 0,
        )),
      );
    });

    test('NextQuestionEvent advances page index', () async {
      getQuestionsUseCase.questions = [q1, q2];
      bloc.add(const LoadQuestionsEvent(interests: ['it'], locale: 'uz'));
      await bloc.stream.skip(1).first;

      bloc.add(const NextQuestionEvent());

      expectLater(
        bloc.stream,
        emits(QuestionsLoaded(
          interests: const ['it'],
          questions: [q1, q2],
          answers: const {},
          currentIndex: 1,
        )),
      );
    });

    test('NextQuestionEvent on last question does nothing', () async {
      getQuestionsUseCase.questions = [q1];
      bloc.add(const LoadQuestionsEvent(interests: ['it'], locale: 'uz'));
      await bloc.stream.skip(1).first;

      bloc.add(const NextQuestionEvent());
      // No extra states should emit since we are on the last question.
      expect(bloc.state, QuestionsLoaded(
        interests: const ['it'],
        questions: [q1],
        answers: const {},
        currentIndex: 0,
      ));
    });

    test('PreviousQuestionEvent decrements page index', () async {
      getQuestionsUseCase.questions = [q1, q2];
      bloc.add(const LoadQuestionsEvent(interests: ['it'], locale: 'uz'));
      await bloc.stream.skip(1).first;

      bloc.add(const NextQuestionEvent());
      await bloc.stream.first; // Now current index is 1

      bloc.add(const PreviousQuestionEvent());

      expectLater(
        bloc.stream,
        emits(QuestionsLoaded(
          interests: const ['it'],
          questions: [q1, q2],
          answers: const {},
          currentIndex: 0,
        )),
      );
    });

    test('PreviousQuestionEvent on first question does nothing', () async {
      getQuestionsUseCase.questions = [q1, q2];
      bloc.add(const LoadQuestionsEvent(interests: ['it'], locale: 'uz'));
      await bloc.stream.skip(1).first;

      bloc.add(const PreviousQuestionEvent());
      expect(bloc.state, QuestionsLoaded(
        interests: const ['it'],
        questions: [q1, q2],
        answers: const {},
        currentIndex: 0,
      ));
    });

    test('SubmitTestEvent submits successfully and emits TestCompleted', () async {
      getQuestionsUseCase.questions = [q1];
      bloc.add(const LoadQuestionsEvent(interests: ['it'], locale: 'uz'));
      await bloc.stream.skip(1).first;

      bloc.add(const SelectAnswerEvent(questionId: 'q1', score: 4));
      await bloc.stream.first;

      submitAnswersUseCase.result = assessmentResult;
      bloc.add(const SubmitTestEvent('uz'));

      expectLater(
        bloc.stream,
        emitsInOrder([
          const TestSubmitting(),
          TestCompleted(assessmentResult),
        ]),
      );
    });

    test('SubmitTestEvent error emits TestError', () async {
      getQuestionsUseCase.questions = [q1];
      bloc.add(const LoadQuestionsEvent(interests: ['it'], locale: 'uz'));
      await bloc.stream.skip(1).first;

      submitAnswersUseCase.shouldThrow = true;
      bloc.add(const SubmitTestEvent('uz'));

      expectLater(
        bloc.stream,
        emitsInOrder([
          const TestSubmitting(),
          TestError('error', previousState: QuestionsLoaded(interests: const ['it'], questions: [q1])),
        ]),
      );
    });

    test('ResetTestEvent returns state to TestInitial', () async {
      getQuestionsUseCase.questions = [q1];
      bloc.add(const LoadQuestionsEvent(interests: ['it'], locale: 'uz'));
      await bloc.stream.skip(1).first;

      bloc.add(const ResetTestEvent());

      expectLater(
        bloc.stream,
        emits(const TestInitial()),
      );
    });

    test('SkipAndSubmitTestEvent auto-fills and submits test successfully', () async {
      getQuestionsUseCase.questions = [q1, q2];
      bloc.add(const LoadQuestionsEvent(interests: ['it'], locale: 'uz'));
      await bloc.stream.skip(1).first;

      submitAnswersUseCase.result = assessmentResult;
      bloc.add(const SkipAndSubmitTestEvent('uz'));

      expectLater(
        bloc.stream,
        emitsInOrder([
          const TestSubmitting(),
          TestCompleted(assessmentResult),
        ]),
      );
    });
  });
}
