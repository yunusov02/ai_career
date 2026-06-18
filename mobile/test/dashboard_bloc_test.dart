import 'package:flutter_test/flutter_test.dart';
import 'package:skillbridge/domain/entities/career.dart';
import 'package:skillbridge/domain/entities/roadmap_step.dart';
import 'package:skillbridge/presentation/blocs/dashboard/dashboard_bloc.dart';
import 'package:skillbridge/presentation/blocs/dashboard/dashboard_event.dart';
import 'package:skillbridge/presentation/blocs/dashboard/dashboard_state.dart';

void main() {
  group('DashboardBloc - Dual-Career Learning Tests', () {
    final career1 = const Career(
      id: 'dev_mobile',
      title: 'Mobile Developer',
      category: 'it',
      emoji: '📱',
      description: 'Creates mobile applications',
      matchPercentage: 95,
      skills: ['Flutter', 'Dart'],
      fitReason: 'Fits well with logic and coding interests',
    );

    final career2 = const Career(
      id: 'design_uiux',
      title: 'UI/UX Designer',
      category: 'design',
      emoji: '🎨',
      description: 'Designs interfaces',
      matchPercentage: 88,
      skills: ['Figma', 'UI Design'],
      fitReason: 'Fits well with creative visual interests',
    );

    final career3 = const Career(
      id: 'pm',
      title: 'Product Manager',
      category: 'business',
      emoji: '💼',
      description: 'Manages products',
      matchPercentage: 80,
      skills: ['Agile', 'Scrum'],
      fitReason: 'Fits business management interests',
    );

    final steps1 = const <RoadmapStep>[
      RoadmapStep(
        stepNumber: 1,
        title: 'Basics',
        description: 'Basics description',
        duration: '2 weeks',
        resources: ['Youtube'],
        topics: ['Variables', 'Types'],
      ),
      RoadmapStep(
        stepNumber: 2,
        title: 'Advanced',
        description: 'Advanced description',
        duration: '3 weeks',
        resources: ['Documentation'],
        topics: ['BLoC', 'RxDart'],
      ),
    ];

    final steps2 = const <RoadmapStep>[
      RoadmapStep(
        stepNumber: 1,
        title: 'Design thinking',
        description: 'Intro description',
        duration: '1 week',
        resources: ['Medium'],
        topics: ['Prototyping'],
      ),
    ];

    test('Initial state is empty', () {
      final bloc = DashboardBloc();
      expect(bloc.state.activeCareers.isEmpty, true);
      expect(bloc.state.selectedCareerId, isNull);
      expect(bloc.state.career, isNull);
      bloc.close();
    });

    test('Can start a journey and select the first career', () {
      final bloc = DashboardBloc();
      bloc.add(StartJourneyEvent(career: career1, steps: steps1));

      expectLater(
        bloc.stream,
        emits(predicate<DashboardState>((state) {
          return state.activeCareers.containsKey('dev_mobile') &&
              state.selectedCareerId == 'dev_mobile' &&
              state.career == career1 &&
              state.steps == steps1 &&
              state.unlockedModules.contains(1);
        })),
      );
    });

    test('Can start a second journey and toggle between them', () async {
      final bloc = DashboardBloc();
      bloc.add(StartJourneyEvent(career: career1, steps: steps1));
      await bloc.stream.first;

      bloc.add(StartJourneyEvent(career: career2, steps: steps2));
      await bloc.stream.first;

      expect(bloc.state.activeCareers.length, 2);
      expect(bloc.state.selectedCareerId, 'design_uiux');
      expect(bloc.state.career, career2);

      // Toggle back to first career
      bloc.add(const SelectActiveCareerEvent('dev_mobile'));
      await bloc.stream.first;

      expect(bloc.state.selectedCareerId, 'dev_mobile');
      expect(bloc.state.career, career1);
      expect(bloc.state.steps, steps1);

      bloc.close();
    });

    test('Cannot exceed 2 active careers', () async {
      final bloc = DashboardBloc();
      bloc.add(StartJourneyEvent(career: career1, steps: steps1));
      await bloc.stream.first;
      bloc.add(StartJourneyEvent(career: career2, steps: steps2));
      await bloc.stream.first;

      // Try starting a third one
      bloc.add(StartJourneyEvent(career: career3, steps: steps2));
      // No state emission should happen because it's ignored
      expect(bloc.state.activeCareers.length, 2);
      expect(bloc.state.activeCareers.containsKey('pm'), false);

      bloc.close();
    });

    test('Resetting removes the selected career and falls back to remaining', () async {
      final bloc = DashboardBloc();
      bloc.add(StartJourneyEvent(career: career1, steps: steps1));
      await bloc.stream.first;
      bloc.add(StartJourneyEvent(career: career2, steps: steps2));
      await bloc.stream.first;

      expect(bloc.state.selectedCareerId, 'design_uiux');

      bloc.add(const ResetJourneyEvent());
      await bloc.stream.first;

      expect(bloc.state.activeCareers.length, 1);
      expect(bloc.state.activeCareers.containsKey('design_uiux'), false);
      expect(bloc.state.selectedCareerId, 'dev_mobile');
      expect(bloc.state.career, career1);

      bloc.close();
    });
  });
}
