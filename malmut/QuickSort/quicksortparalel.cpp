#include <iostream>
#include <vector>
#include <future>
#include <algorithm>
#include "../MatrixThreads/timer.hh"

using namespace std;

vector<int> quickSortSec(vector<int> numbers) {
    if (numbers.size() > 1) {
        int pivot = numbers[0];
        vector<int> left = {};
        vector<int> right = {};
        for (auto i : numbers) {
            i != pivot ? i < pivot ? left.push_back(i) : right.push_back(i) : void();
        }
        vector<int> quickLeft = quickSortSec(left);
        vector<int> quickRight = quickSortSec(right);
        vector<int> result = {};
        result.insert(result.end(), quickLeft.begin(), quickLeft.end());
        result.push_back(pivot);
        result.insert(result.end(), quickRight.begin(), quickRight.end());
        return result;
    } else {
        return numbers;
    }
}

vector<int> quickSortParalel(vector<int> numbers) {
    if (numbers.size() > 1) {
        int pivot = numbers[0];
        vector<int> left = {};
        vector<int> right = {};
        for (auto i : numbers) {
            i != pivot ? i < pivot ? left.push_back(i) : right.push_back(i) : void();
        }
        auto futureLeft = async(launch::async, quickSortParalel, left);
        auto futureRight = async(launch::async, quickSortParalel, right);
        vector<int> result = {};
        vector<int> quickLeft = futureLeft.get();
        vector<int> quickRight = futureRight.get();
        result.insert(result.end(), quickLeft.begin(), quickLeft.end());
        result.push_back(pivot);
        result.insert(result.end(), quickRight.begin(), quickRight.end());
        return result;
    } else {
        return numbers;
    }
}

int verifyNumber(vector<int> data, int number) {
    if (find(data.begin(), data.end(), number) != data.end()) {
        int number = rand() % 11000 + 1;
        verifyNumber(data, number);
    } else {
        return number;
    }
}

int main() {
    vector<int> data = {};
    for (size_t i = 0; i < 10000; i++){
        int number = verifyNumber(data, rand() % 11000 + 1);
        //int number = rand() % 11000 + 1;
        data.push_back(number);
    }
    Timer t;
    vector<int> resultSec = quickSortSec(data);
    cout << "Tiempo demorado secuencial: " << t.elapsed() << endl;
    getchar();
    for (auto i : resultSec){
        cout << i << endl;
    }
    Timer u;
    vector<int> resultParalel = quickSortParalel(data);
    cout << "Tiempo demorado paralelo: " << u.elapsed() << endl;
    getchar();
    for (auto i : resultParalel){
        cout << i << endl;
    }
    return 0;
}