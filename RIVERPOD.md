# Riverpod Guide

---

## **1. Providers in Riverpod**

Providers are fundamental building blocks in Riverpod. They define how to create and manage pieces of state.

### **1.1. `Provider` (Read-Only State)**
Used for immutable values or computed values.

```dart
// Define a read-only provider that returns a string
final nameProvider = Provider((ref) => 'Riverpod Example');

void main() {
  // Create a container to manually read the provider
  final container = ProviderContainer();
  
  // Read and print the value of the provider
  print(container.read(nameProvider)); // Output: Riverpod Example
}
```

**Explanation:**
- `Provider` creates a simple, immutable state.
- `ProviderContainer()` allows reading providers outside a widget tree.
- `read(nameProvider)` fetches the value.

---

## **2. Reading and Watching Providers**

### **2.1. Using `ref.watch` (Rebuild on Change)**

```dart
// A state provider that holds an integer
final counterProvider = StateProvider((ref) => 0);

class CounterWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch provider state - rebuilds UI when state changes
    final count = ref.watch(counterProvider);
    
    return Text('Counter: \$count');
  }
}
```

**Explanation:**
- `StateProvider` allows modifying state.
- `ref.watch(counterProvider)` rebuilds the widget when `counterProvider` changes.
- The UI updates dynamically when the counter is modified.

### **2.2. Using `ref.read` (Read Once, No Rebuilds)**

```dart
void incrementCounter(WidgetRef ref) {
  // Read the provider's current state and increment it
  ref.read(counterProvider.notifier).state++;
}
```

**Explanation:**
- `ref.read(counterProvider)` accesses the provider's state **without rebuilding UI**.
- `.notifier` gets the state controller to modify values.

---

## **3. Managing State with Notifiers**

### **3.1. `StateProvider` (Simple State Management)**

```dart
final counterProvider = StateProvider<int>((ref) => 0);

void incrementCounter(WidgetRef ref) {
  ref.read(counterProvider.notifier).state++;
}
```

**Explanation:**
- `StateProvider<int>` initializes a state with `0`.
- `.notifier.state++` modifies the state.

### **3.2. `StateNotifierProvider` (Complex State Management)**

```dart
class CounterNotifier extends StateNotifier<int> {
  CounterNotifier() : super(0); // Initial state is 0

  void increment() => state++; // Increments state
}

final counterProvider = StateNotifierProvider<CounterNotifier, int>((ref) {
  return CounterNotifier();
});
```

**Explanation:**
- `StateNotifier<int>` maintains state with methods (`increment`).
- `StateNotifierProvider` connects `CounterNotifier` to the UI.
- `state` is automatically updated and reactive.

---

## **4. Handling Asynchronous Data**

### **4.1. `FutureProvider`**
Handles async values such as fetching data from an API.

```dart
final userProvider = FutureProvider<String>((ref) async {
  await Future.delayed(Duration(seconds: 2));
  return 'User Loaded';
});
```

**Explanation:**
- `FutureProvider<String>` fetches async data.
- Simulated delay (`Future.delayed`) before returning data.

### **4.2. Using `AsyncValue` to Handle Loading, Error, and Data**

```dart
class UserWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAsync = ref.watch(userProvider);

    return userAsync.when(
      data: (data) => Text(data),
      loading: () => CircularProgressIndicator(),
      error: (err, stack) => Text('Error: \$err'),
    );
  }
}
```

**Explanation:**
- `ref.watch(userProvider)` watches the future state.
- `.when()` handles `data`, `loading`, and `error` cases.

---

## **5. Riverpod Callbacks & Listening**

### **5.1. `ref.listen` (Listening for Changes Without Rebuilding UI)**

```dart
class ExampleWidget extends ConsumerStatefulWidget {
  @override
  _ExampleWidgetState createState() => _ExampleWidgetState();
}

class _ExampleWidgetState extends ConsumerState<ExampleWidget> {
  @override
  void initState() {
    super.initState();
    ref.listen<int>(counterProvider, (prev, next) {
      print('Counter changed from \$prev to \$next');
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container();
  }
}
```

**Explanation:**
- `ref.listen()` observes state changes without affecting UI rebuilds.
- Useful for triggering side effects (logging, animations, etc.).

---

## **6. Sending Events with `StreamProvider`**

Used for managing real-time updates like WebSockets.

```dart
final streamProvider = StreamProvider<int>((ref) async* {
  for (int i = 0; i < 10; i++) {
    await Future.delayed(Duration(seconds: 1));
    yield i;
  }
});
```

**Explanation:**
- `StreamProvider<int>` emits a new value every second.
- `yield` sends the next value in the stream.

```dart
class StreamWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final streamAsync = ref.watch(streamProvider);

    return streamAsync.when(
      data: (value) => Text('Stream: \$value'),
      loading: () => CircularProgressIndicator(),
      error: (err, stack) => Text('Error: \$err'),
    );
  }
}
```

**Explanation:**
- Watches the stream and updates UI when data arrives.
- Uses `.when()` to handle data, loading, and errors.

---

## **7. Using `ref.invalidate` to Refresh Data**

```dart
void refreshData(WidgetRef ref) {
  ref.invalidate(userProvider);
}
```

**Explanation:**
- `ref.invalidate()` forces a provider to recompute its state.
- Useful for refreshing API data or resetting state.

---

