#include <iostream>
#include <future>
#include "../MatrixThreads/timer.hh"

using namespace std;

double fibonacci(int n) {
    if (n < 2) return 1.0;
    else {
        future<double> a = async(launch::async, fibonacci, n-1);
        future<double> b = async(launch::async, fibonacci, n-2);
        return a.get() + b.get();
    }
}

int main() {
    int number;
    cout << "Ingrese el numero: ";
    cin >> number;
    Timer t;
    cout << "Resulado: " << fibonacci(number) << endl;
    cout << "Tiempo demorado: " << t.elapsed() << endl; 
    return 0;
}