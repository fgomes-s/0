/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memchr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/10/28 15:33:00 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/10/28 15:47:19 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */



#include "stddef.h"

 void *ft_memchr(const void *s, int c, size_t n)
{
    size_t x;
    unsigned char *ptr;
    
    x = 0;
    ptr = (unsigned char *)s;
    while (x < n)
    {
        if (ptr[x] == (unsigned char)c)
        {
            return (&ptr[x]);
        }
        x++;
    }
    return (NULL);
}
