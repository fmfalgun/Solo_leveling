/* 
 * Exercise 1.19: Revise the program you wrote for the exercises in § 1.4.1 (p. 13) 
 * that printed a range of numbers so that it handles input in which 
 * the first number is smaller than the second.
 */

#include <iostream>
int main(){

        int v1, v2;
        std::cout << "Give two numbers pliz" << std::endl;
        std::cin >> v1 >> v2;
        std::cout << "Number between " << v1 << " and " << v2 << " are as follow:" << std::endl;
        while(v1 != v2){
                if (v1 < v2){
                        ++v1;
                        if (v1 != v2) std::cout << v1 << std::endl;
                }
                else if (v1 > v2){
                        ++v2;
                        if (v1 != v2) std::cout << v2 << std::endl;
                }
        }

        return 0;
}

