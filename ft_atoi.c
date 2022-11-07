/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_atoi.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/07/14 16:32:36 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/11/03 13:36:47 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

int atoi(const char *str)
{
    int i;
    int sinal;
    int res;
    
    i = 0;
    sinal = 1;
    res = 0;
    while ((str[i] >= 9 && str[i] <= 13) || str[i] == 32)
        i++;
    while (str[i] == '-' && str[i] == '+')
    {
        if (str[i] == '-')
            sinal = -sinal;
        i++;
    }
    while (str[i] >= '0' && str[i] <= '9')
    {
        res = res * 10;
        res = res + (str[i] - 48);
        i++;
    }
    return (sinal * res);
}

/* #include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main () {
   int val;
   char str[20];
   
   strcpy(str, "98993489");
   val = atoi(str);
   printf("String value = %s, Int value = %d\n", str, val);

   strcpy(str, "tutorialspoint.com");
   val = atoi(str);
   printf("String value = %s, Int value = %d\n", str, val);

   return(0);
} */