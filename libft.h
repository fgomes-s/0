/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   libft.h                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2022/10/25 18:10:40 by fgomes-s          #+#    #+#             */
/*   Updated: 2022/10/26 16:11:20 by fgomes-s         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */




#include <string.h>
#include <stdlib.h>

#include <unistd.h>
#include <stdio.h>
#include <ctype.h>
#include <strings.h>

int	ft_atoi(char *str);
void ft_bzero(void *s, size_t n);
int ft_isalnum(int c);
int ft_isalpha(int c);
int ft_isascii(int c);
int ft_isdigit(int c);
char *ft_itoa(int n);
char *ft_substr(char const *s, unsigned int start, size_t len);
char *ft_strjoin(char const *s1, char const *s2);
char *ft_strtrim(char const *s1, char const *set);
char **ft_split(char const *s, char c);
char *ft_itoa(int n);
char *ft_strmapi(char const *s, char (*f)(unsigned int, char));
void ft_striteri(char *s, void (*f)(unsigned int, char*));
void ft_putchar_fd(char c, int fd);
void ft_putstr_fd(char *s, int fd);
void ft_putendl_fd(char *s, int fd);
void ft_putnbr_fd(int n, int fd);
t_list *ft_lstnew(void *content);
void ft_lstadd_front(t_list **lst, t_list *new);
int ft_lstsize (t_list *lst);
t_list *ft_lstlast(t_list *lst);
void ft_lstadd_back(t_list **lst, t_list *new);
void ft_lstdelone(t_list *lst, void (*del)(void*));
void ft_lstclear(t_list **lst, void (*del)(void *));
void ft_lstiter(t_list *lst, void (*f)(void *));
t_list *ft_lstmap(t_list *lst, void *(*f)(void *), void (*del)(void *));
int ft_atoi(const char *nptr);
char * ft_strnstr(const char *big, const char *little, size_t len);
int ft_memcmp(const void *str1, const void *str2, size_t n)
void *ft_memchr(const void *str, int c, size_t n)
int ft_strncmp(const char *str1, const char *str2, size_t n)
char *ft_strrchr(const char *str, int c)
char *ft_strchr(const char *str, int c)
int ft_tolower(int argument);
int ft_toupper(int ch);
size_t ft_strlcat(char *dest, const char *src, size_t size);
size_t ft_strlcpy(char *dest, const char *src, size_t size);
void *ft_memmove(void *str1, const void *str2, size_t n)
void *ft_memcpy(void *dest, const void * src, size_t n)
void ft_bzero(void *s, size_t n);
void *ft_memset(void *str, int c, size_t n)
size_t ft_strlen(const char *str)
int ft_isprint(int c);











