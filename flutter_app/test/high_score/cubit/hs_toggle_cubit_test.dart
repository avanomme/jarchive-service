import 'package:bloc_test/bloc_test.dart';
import 'package:test/test.dart';
import 'package:winning_streak/high_score/cubit/hs_toggle_cubit.dart';

//tests relating to the HSToggleCubit
//no mocking the cubit we test the methods directly on the real cubit
//the state is a simple bool so no corresponding tests relating to the State
void main() {

  group('HSToggleCubit', () {

    test('initial state is correct LOCAL', () {
      final toggleCubit = HSToggleCubit(HSToggleCubit.LOCAL);
      expect(toggleCubit.state,HSToggleCubit.LOCAL);
    });

    test('initial state is correct GLOBAL', () {
      final toggleCubit = HSToggleCubit(HSToggleCubit.GLOBAL);
      expect(toggleCubit.state,HSToggleCubit.GLOBAL);
    });

    group( 'toggle local/global', () {
      blocTest<HSToggleCubit, bool>(
          'emits Global when toggled local to global',
           build: () => HSToggleCubit(HSToggleCubit.LOCAL),
           act: (cubit) => cubit.toggle(HSToggleCubit.GLOBAL),
           expect: () => <bool> [
            HSToggleCubit.GLOBAL,
           ]
      );

      blocTest<HSToggleCubit, bool>(
          'emits local when created local and toggled to local',
          build: () => HSToggleCubit(HSToggleCubit.LOCAL),
          act: (cubit) => cubit.toggle(HSToggleCubit.LOCAL),
          expect: () => <bool> [
            HSToggleCubit.LOCAL,
          ]
      );

      blocTest<HSToggleCubit, bool>(
          'emits Local when toggled global to local',
          build: () => HSToggleCubit(HSToggleCubit.GLOBAL),
          act: (cubit) => cubit.toggle(HSToggleCubit.LOCAL),
          expect: () => <bool> [
            HSToggleCubit.LOCAL,
          ]
      );

      blocTest<HSToggleCubit, bool>(
          'emits nothing on same same toggle',
          build: () => HSToggleCubit(HSToggleCubit.GLOBAL),
          act: (cubit) => cubit..toggle(HSToggleCubit.GLOBAL)
                               ..toggle(HSToggleCubit.GLOBAL),
          expect: () => <bool> [
            HSToggleCubit.GLOBAL
            //just one toggle emitted
          ]
      );

      blocTest<HSToggleCubit, bool>(
          'emits local global local on multi toggles',
          build: () => HSToggleCubit(HSToggleCubit.GLOBAL),
          act: (cubit) => cubit..toggle(HSToggleCubit.LOCAL)
                               ..toggle(HSToggleCubit.GLOBAL)
                               ..toggle(HSToggleCubit.LOCAL)
                               ..toggle(HSToggleCubit.LOCAL),
          expect: () => <bool> [
            HSToggleCubit.LOCAL,
            HSToggleCubit.GLOBAL,
            HSToggleCubit.LOCAL,
          ]
      );

    });//end of 'toggle local/global group
    
  });


}