#include <iostream>
#include <thread>
#include <string>
#include "timer.hh"
#include "Matrix.hh"

// Single thread matrix multiplication
Matrix mult(const Matrix& a, const Matrix& b) {
  Matrix result(a.size());

  for(int r = 0; r < a.size(); r++ ) {
    for (int c = 0; c < a.size(); c++) {
      for (int rm = 0; rm < b.size(); rm++) {
        result.at(r, c) += a.at(r, rm) * b.at(rm, c);
      }
    }
  }

  return result;
}

void computeCell(const Matrix& a, const Matrix& b, size_t ra, size_t cb, double& result) {
  result = 0.0;
  for (size_t nc = 0; nc < b.size(); nc++) {
    result += a.at(ra, nc) * b.at(nc, cb);
  }
}

void computeCol(const Matrix& a, const Matrix& b, size_t col, Matrix& result) {
  for (size_t r = 0; r < a.size(); r++)
  {
    for (size_t c = 0; c < a.size(); c++)
    {
      result.at(r, col) += a.at(r, c) * b.at(c, col);
    }
  }
  
}

Matrix mult2(const Matrix& a, const Matrix& b) {
  Matrix result(a.size());
  vector<thread> threads;

  for(int r = 0; r < a.size(); r++ ) {
    for (int c = 0; c < a.size(); c++) {
      // for (int rm = 0; rm < b.size(); rm++) {
      //   result.at(r, c) += a.at(r, rm) * b.at(rm, c);
      // }
      double re;
      threads.push_back(thread(computeCell, cref(a), cref(b), r, c, ref(re)));
      result.at(r,c) = re;
    }
  }
  for(thread& t : threads ) {
    t.join();
  }
  return result;
}

Matrix mult3(const Matrix& a, const Matrix& b) {
  Matrix result(a.size());
  vector<thread> threads;
  for (size_t c = 0; c < b.size(); c++)
  {
    threads.push_back(thread(computeCol, cref(a), cref(b), c, ref(result)));
  }
  for(thread& t: threads)
    t.join();
  return result;
}

void bench() {
  for (int i = 100; i < 5000;) {
    Matrix m(i);
    m.fill();
    Matrix n(i);
    n.fill();

    cout << i;

    Timer t;
    Matrix r = mult(m, n);
    cout << " " << t.elapsed();     

    Timer u;
    Matrix ur = mult3(m, n);
    cout << " " << u.elapsed();     

    cout << endl;
    i = i + 10;
  }
}

void say(const string& s ) {
  cout << "Hola " << s << endl;
}

int main() {
  // vector<thread> threads;
  // threads.push_back(thread(say, "Gustavo"));  // 1
  // threads.push_back(thread(say, "David"));    // 2
  // threads.push_back(thread(say, "Stiven"));   // 3
  
  // for(thread& t : threads ) {
  //   t.join();
  // }
  bench();
}
