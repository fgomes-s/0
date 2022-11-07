/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_calloc.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/11/07 13:59:28 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/11/07 14:15:51 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

void *calloc(size_t nitems, size_t size)
{
	void	*ptr;

	if (size && SIZE_MAX / size < nitems)
		return (NULL);
	ptr = malloc(nitems * size);
	if (!ptr)
		return (NULL);
	ft_bzero(ptr, nitems * size);
	return (ptr);
}