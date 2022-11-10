/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memset.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/10/28 12:20:45 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/11/10 14:35:50 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void *ft_memset(void *str, int c, size_t n)
{
    unsigned char a;
    long int i;

    i = 0;
    a = c;
    while(i < n)
    {
        ((unsigned char *)str)[i] = a;
        i++;
    }
    return (str);
}

#include <stdio.h>
int main()
{
    char str[] = "abc";
    printf("%s\n",str);
    ft_memset(str,33,1);
    printf("%s", str);
}