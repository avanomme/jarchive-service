
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:winning_streak/high_score/cubit/hs_toggle_cubit.dart';
import 'package:winning_streak/high_score/view/high_score_page.dart';
import 'package:winning_streak/high_score/view/high_score_view.dart';

// Mock class
class MockHSToggleCubit extends MockCubit<bool> implements HSToggleCubit {}

//Test the HighScorePage
void main() {

  //tests on the HighScorePage in General
  group('HighScorePage', ()
  {
    late HSToggleCubit toggleCubit;

    setUp(() {
      //create the MockedCubit
      toggleCubit = MockHSToggleCubit();
    });

    testWidgets('renders highscore view', (WidgetTester tester) async {
      //if state is called return LOCAL
      when(() => toggleCubit.state).thenReturn(HSToggleCubit.LOCAL);

      // Build our app and trigger a frame.
      await tester.pumpWidget(
          BlocProvider.value(
            value: toggleCubit,
            child: MaterialApp(home: HighScorePage()),
          )
      );
      //launching HighScorePage should create 1xHighScoreView
      expect(find.byType(HighScoreView), findsOneWidget);
    });

    testWidgets('renders bottom navigation bar', (WidgetTester tester) async {
      //if state is called return LOCAL
      when(() => toggleCubit.state).thenReturn(HSToggleCubit.LOCAL);

      // Build our app and trigger a frame.
      await tester.pumpWidget(
          BlocProvider.value(
            value: toggleCubit,
            child: MaterialApp(home: HighScorePage()),
          )
      );
      //finds one navigation bar
      expect(find.byType(CustomBottomNavigationBar), findsOneWidget);

    });

    testWidgets('bottom nav bar has Local and Global', (WidgetTester tester) async {
      //if state is called return LOCAL
      when(() => toggleCubit.state).thenReturn(HSToggleCubit.LOCAL);

      // Build just the bottom nav bar
      await tester.pumpWidget(
          BlocProvider.value(
            value: toggleCubit,
            child: MaterialApp(home: Scaffold(bottomNavigationBar:CustomBottomNavigationBar())),
          )
      );
      //finds one navigation bar
      expect(find.text('Local'), findsOneWidget);
      expect(find.text('Global'), findsOneWidget);
    });

    testWidgets('hs view accesses cubit state', (WidgetTester tester) async {
      //if state is called return LOCAL
      when(() => toggleCubit.state).thenReturn(HSToggleCubit.LOCAL);

      // Build our app and trigger a frame.
      await tester.pumpWidget(
          BlocProvider.value(
            value: toggleCubit,
            child: MaterialApp(home: HighScorePage()),
          )
      );
      //calls state
      verify(()=>toggleCubit.state);
    });

    testWidgets('bottom nav bar has current index = local', (WidgetTester tester) async {
      //if state is called return LOCAL
      when(() => toggleCubit.state).thenReturn(HSToggleCubit.LOCAL);
      // Build just the bottom nav bar
      await tester.pumpWidget(
          BlocProvider.value(
            value: toggleCubit,
            child: MaterialApp(home: Scaffold(bottomNavigationBar:CustomBottomNavigationBar())),
          )
      );

      Element candidate = find.byType(BottomNavigationBar,skipOffstage: true).evaluate().first;
      final castWidget = candidate.widget as BottomNavigationBar;
      expect(castWidget.items[castWidget.currentIndex].label, "Local");
    });


    testWidgets('bottom nav bar has current index = global', (WidgetTester tester) async {
      //if state is called return GLOBAL
      when(() => toggleCubit.state).thenReturn(HSToggleCubit.GLOBAL);
      // Build just the bottom nav bar
      await tester.pumpWidget(
          BlocProvider.value(
            value: toggleCubit,
            child: MaterialApp(home: Scaffold(bottomNavigationBar:CustomBottomNavigationBar())),
          )
      );

      Element candidate = find.byType(BottomNavigationBar,skipOffstage: true).evaluate().first;

      final castWidget = candidate.widget as BottomNavigationBar;
      expect(castWidget.items[castWidget.currentIndex].label, "Global");
    });

    testWidgets('bottom nav has current index = LOCAL', (WidgetTester tester) async {
      //if state is called return false
      when(() => toggleCubit.state).thenReturn(HSToggleCubit.LOCAL);
      // Build just the bottom nav bar
      await tester.pumpWidget(
          BlocProvider.value(
            value: toggleCubit,
            child: MaterialApp(home: Scaffold(bottomNavigationBar:CustomBottomNavigationBar())),
          )
      );

      Element candidate = find.byType(BottomNavigationBar,skipOffstage: true).evaluate().first;
      final castWidget = candidate.widget as BottomNavigationBar;
      expect(castWidget.items[castWidget.currentIndex].label, "Local");
    });

    testWidgets('verify tapping global=> toggle(GLOBAL)', (WidgetTester tester) async {
      //if state is called return false
      when(() => toggleCubit.state).thenReturn(HSToggleCubit.LOCAL);
      // Build just the bottom nav bar
      await tester.pumpWidget(
          BlocProvider.value(
            value: toggleCubit,
            child: MaterialApp(home: HighScorePage()),
          )
      );
      //tap the global tab
      await tester.tap(find.byIcon(CustomBottomNavigationBar.icon_global));

      //rebuild
      await tester.pump();

      //verify toggle has been called with GLOBAL parameter
      verify(()=>toggleCubit.toggle(HSToggleCubit.GLOBAL));

    });

    testWidgets('verify tapping global=> toggle(GLOBAL) only once',
                (WidgetTester tester) async {
      //if state is called return LOCAL
      when(() => toggleCubit.state).thenReturn(HSToggleCubit.LOCAL);
      // Build just the bottom nav bar
      await tester.pumpWidget(
          BlocProvider.value(
            value: toggleCubit,
            child: MaterialApp(home: HighScorePage()),
          )
      );
      //tap the global tab
      await tester.tap(find.byIcon(CustomBottomNavigationBar.icon_global));

      //rebuild
      await tester.pump();
      //verify toggle has been called with GLOBAL parameter
      verify(()=>toggleCubit.toggle(HSToggleCubit.GLOBAL)).called(1);
    });

    testWidgets('verify tapping global=> toggle(LOCAL) not called', (WidgetTester tester) async {
      //if state is called return false
      when(() => toggleCubit.state).thenReturn(HSToggleCubit.LOCAL);
      // Build just the bottom nav bar
      await tester.pumpWidget(
          BlocProvider.value(
            value: toggleCubit,
            child: MaterialApp(home: HighScorePage()),
          )
      );
      //tap the global tab
      await tester.tap(find.byIcon(CustomBottomNavigationBar.icon_global));

      //rebuild
      await tester.pump();

      //verify toggle has NEVER been called with LOCAL
      verifyNever(()=>toggleCubit.toggle(HSToggleCubit.LOCAL));

    });

    testWidgets('verify tapping local=> toggle(LOCAL) only once', (WidgetTester tester) async {
      //if state is called return false
      when(() => toggleCubit.state).thenReturn(HSToggleCubit.LOCAL);
      // Build just the bottom nav bar
      await tester.pumpWidget(
          BlocProvider.value(
            value: toggleCubit,
            child: MaterialApp(home: HighScorePage()),
          )
      );
      //tap the global tab
      await tester.tap(find.byIcon(CustomBottomNavigationBar.icon_local));

      //rebuild
      await tester.pump();

      //verify toggle has been called with GLOBAL parameter
      verify(()=>toggleCubit.toggle(HSToggleCubit.LOCAL)).called(1);
    });


    testWidgets('verify tapping local=> toggle(GLOBAL) NEVER', (WidgetTester tester) async {
      //if state is called return false
      when(() => toggleCubit.state).thenReturn(HSToggleCubit.LOCAL);
      // Build just the bottom nav bar
      await tester.pumpWidget(
          BlocProvider.value(
            value: toggleCubit,
            child: MaterialApp(home: HighScorePage()),
          )
      );
      //tap the global tab
      await tester.tap(find.byIcon(CustomBottomNavigationBar.icon_local));

      //rebuild
      await tester.pump();

      //verify toggle has been called with GLOBAL parameter
      verifyNever(()=>toggleCubit.toggle(HSToggleCubit.GLOBAL));

    });
  });//end of group HighScorePage

}