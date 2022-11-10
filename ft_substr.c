/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_substr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/11/08 11:21:04 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/11/10 14:56:21 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char    *ft_substr(char const *src, unsigned int start, size_t len)
{
    unsigned int i;
    unsigned int j;
    char *dest;
    
    if (ft_strlen(src) < len)
        dest =(char *)malloc(sizeof(char) * (ft_strlen(src) + 1));
    /*ver o tamanho e depois alocar a memoria da dest (+1 pelo caracter nulo extra) */
    else if (start > ft_strlen(src))
        dest = (char *)malloc(sizeof(char) * 1);