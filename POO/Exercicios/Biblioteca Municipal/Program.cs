using Biblioteca_Municipal.Model;

namespace Biblioteca_Municipal
{
    internal class Program
    {
        static List<Livro> livros = new List<Livro>();
        static List<Membro> membros = new List<Membro>();
        static List<Emprestimo> emprestimos = new List<Emprestimo>();

        static void Main(string[] args)
        {
            int opcao;

            do
            {
                Console.WriteLine("\n===== BIBLIOTECA =====");
                Console.WriteLine("1. Cadastrar Livro");
                Console.WriteLine("2. Cadastrar Membro");
                Console.WriteLine("3. Fazer Empréstimo");
                Console.WriteLine("4. Devolver Livro");
                Console.WriteLine("5. Listar Livros");
                Console.WriteLine("6. Listar Membros");
                Console.WriteLine("0. Sair");
                Console.Write("Escolha: ");

                opcao = int.Parse(Console.ReadLine());

                switch (opcao)
                {
                    case 1: CadastrarLivro(); break;
                    case 2: CadastrarMembro(); break;
                    case 3: FazerEmprestimo(); break;
                    case 4: DevolverLivro(); break;
                    case 5: ListarLivros(); break;
                    case 6: ListarMembros(); break;
                }

            } while (opcao != 0);
        }

        static void CadastrarLivro()
        {
            Livro livro = new Livro();

            Console.Write("ISBN: ");
            livro.Isbn = Console.ReadLine();

            Console.Write("Título: ");
            livro.Titulo = Console.ReadLine();

            Console.Write("Autor: ");
            livro.Autor = Console.ReadLine();

            Console.Write("Ano: ");
            livro.AnoPublicacao = int.Parse(Console.ReadLine());

            livro.Disponivel = true;

            livros.Add(livro);

            Console.WriteLine("Livro cadastrado com sucesso!");
        }

        static void CadastrarMembro()
        {
            Membro membro = new Membro();

            Console.Write("ID: ");
            membro.IdMembro = int.Parse(Console.ReadLine());

            Console.Write("Nome: ");
            membro.Nome = Console.ReadLine();

            Console.Write("Email: ");
            membro.Email = Console.ReadLine();

            membro.DataRegisto = DateTime.Now;

            membros.Add(membro);

            Console.WriteLine("Membro cadastrado!");
        }

        static void FazerEmprestimo()
        {
            if (livros.Count == 0 || membros.Count == 0)
            {
                Console.WriteLine("Cadastre livros e membros primeiro!");
                return;
            }

            Console.WriteLine("\nEscolha o livro:");
            for (int i = 0; i < livros.Count; i++)
            {
                Console.WriteLine($"{i} - {livros[i].Titulo} ({(livros[i].Disponivel ? "Disponível" : "Indisponível")})");
            }

            int indexLivro = int.Parse(Console.ReadLine());
            Livro livro = livros[indexLivro];

            if (!livro.Disponivel)
            {
                Console.WriteLine("Livro indisponível!");
                return;
            }

            Console.WriteLine("\nEscolha o membro:");
            for (int i = 0; i < membros.Count; i++)
            {
                Console.WriteLine($"{i} - {membros[i].Nome}");
            }

            int indexMembro = int.Parse(Console.ReadLine());
            Membro membro = membros[indexMembro];

            Emprestimo emp = new Emprestimo();
            emp.Id = emprestimos.Count + 1;
            emp.Livro = livro;
            emp.Membro = membro;
            emp.DataEmprestimo = DateTime.Now;
            emp.DataDevolucaoPrevista = DateTime.Now.AddDays(7);

            livro.MarcarEmprestado();

            emprestimos.Add(emp);

            Console.WriteLine("Empréstimo realizado!");
        }

        static void DevolverLivro()
        {
            Console.WriteLine("\nLista de Empréstimos:");

            for (int i = 0; i < emprestimos.Count; i++)
            {
                Console.WriteLine($"{i} - {emprestimos[i].Livro.Titulo}");
            }

            int index = int.Parse(Console.ReadLine());

            Emprestimo emp = emprestimos[index];

            emp.RegistarDevolucao();

            Console.WriteLine("Livro devolvido!");

            int atraso = emp.CalcularAtraso();
            if (atraso > 0)
            {
                double multa = emp.CalcularMulta(atraso);
                Console.WriteLine($"Atraso: {atraso} dias | Multa: {multa}");
            }
        }

        static void ListarLivros()
        {
            Console.WriteLine("\n=== LIVROS ===");

            foreach (var l in livros)
            {
                Console.WriteLine($"{l.Titulo} - {l.Autor} - {(l.Disponivel ? "Disponível" : "Emprestado")}");
            }
        }

        static void ListarMembros()
        {
            Console.WriteLine("\n=== MEMBROS ===");

            foreach (var m in membros)
            {
                Console.WriteLine($"{m.IdMembro} - {m.Nome}");
            }
        }
    }
}
