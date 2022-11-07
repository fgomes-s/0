/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strchr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/10/28 16:17:58 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/11/02 15:55:45 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "stddef.h"
#include <stdio.h>

char *ft_strchr(const char *str, int c)
{
    while (*str != '\0')
    {
        if (*str == c) return (char *) str;
        str++;
    }
    return(NULL);
}
