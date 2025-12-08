/*
 * Exercise 1.13: Rewrite the first two exercises from § 1.4.1 (p. 13) using for loops.
 */

#include <iostream>
int main(){

	// exe 1.9 
        int sum = 50;
	for (int i=51; i<=100;i++)
		sum += i;
        std::cout << "Sum of 50 to 100 inclusive is "
                << sum << std::endl;

	// exe 1.10
        for(int num = 10; num>=0; num--){
                std::cout << num << std::endl;
        }


        return 0;
}
           
