/*
 * Exercise 2.10: What are the initial values, if any, of each of the following variables?
 * 	std::string global_str;
 * 	int global_int;
 * 	int main()
 * 	{
 * 		int local_int;
 * 		std::string local_str;
 * 	}
 */

// Expected Answer: 
// 	gloabl_str = ""
// 	global_int = 0
// 	local_str = ""
// 	local_int = 0

#include <iostream>
std::string global_str;
int global_int;
int main()
{
	int local_int;
	std::string local_str;
	std::cout << global_str << std::endl;
	std::cout << global_int << std::endl;
	std::cout << local_str << std::endl;
	std::cout << local_int << std::endl;
	return 0;
}

// result
//
//0
//
//32767
//
