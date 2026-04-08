using Loja_Online___Catálogo_de_Produtos.Model;

namespace Loja_Online___Catálogo_de_Produtos
{
    public class Program
    {
        static List<Produto> produtos = new List<Produto>();
        static Carrinho carrinho = new Carrinho();
        static Cliente cliente = new Cliente();

        static void Main()
        {
            int opcao = 0;

            do
            {
                Console.WriteLine("\n===== LOJA ONLINE =====");
                Console.WriteLine("1 - Criar Cliente");
                Console.WriteLine("2 - Adicionar Produto Físico");
                Console.WriteLine("3 - Adicionar Produto Digital");
                Console.WriteLine("4 - Listar Produtos");
                Console.WriteLine("5 - Adicionar Produto ao Carrinho");
                Console.WriteLine("6 - Ver Carrinho");
                Console.WriteLine("0 - Sair");

                Console.Write("Escolha: ");
                opcao = int.Parse(Console.ReadLine());

                switch (opcao)
                {
                    case 1:
                        CriarCliente();
                        break;

                    case 2:
                        CriarProdutoFisico();
                        break;

                    case 3:
                        CriarProdutoDigital();
                        break;

                    case 4:
                        ListarProdutos();
                        break;

                    case 5:
                        AdicionarAoCarrinho();
                        break;

                    case 6:
                        VerCarrinho();
                        break;
                }

            } while (opcao != 0);
        }

        static void CriarCliente()
        {
            Console.Write("Nome: ");
            cliente.Nome = Console.ReadLine();

            Console.Write("Email: ");
            cliente.Email = Console.ReadLine();

            Console.Write("Morada: ");
            cliente.Morada = Console.ReadLine();

            cliente.Carrinho = carrinho;

            Console.WriteLine("Cliente criado com sucesso!");
        }

        static void CriarProdutoFisico()
        {
            ProdutoFisico p = new ProdutoFisico();

            Console.Write("ID: ");
            p.Id = int.Parse(Console.ReadLine());

            Console.Write("Nome: ");
            p.Nome = Console.ReadLine();

            Console.Write("Descricao: ");
            p.Descricao = Console.ReadLine();

            Console.Write("Preço: ");
            p.Preco = double.Parse(Console.ReadLine());

            Console.Write("Stock: ");
            p.Stock = int.Parse(Console.ReadLine());

            Console.Write("Peso: ");
            p.Peso = double.Parse(Console.ReadLine());

            Console.Write("Dimensoes: ");
            p.Dimensoes = Console.ReadLine();

            produtos.Add(p);

            Console.WriteLine("Produto físico adicionado!");
        }

        static void CriarProdutoDigital()
        {
            ProdutoDigital p = new ProdutoDigital();

            Console.Write("ID: ");
            p.Id = int.Parse(Console.ReadLine());

            Console.Write("Nome: ");
            p.Nome = Console.ReadLine();

            Console.Write("Descricao: ");
            p.Descricao = Console.ReadLine();

            Console.Write("Preço: ");
            p.Preco = double.Parse(Console.ReadLine());

            Console.Write("Stock: ");
            p.Stock = int.Parse(Console.ReadLine());

            Console.Write("Tamanho MB: ");
            p.TamanhoMB = double.Parse(Console.ReadLine());

            Console.Write("Formato: ");
            p.FormatoFicheiro = Console.ReadLine();

            produtos.Add(p);

            Console.WriteLine("Produto digital adicionado!");
        }

        static void ListarProdutos()
        {
            Console.WriteLine("\n--- PRODUTOS ---");

            foreach (var p in produtos)
            {
                Console.WriteLine($"ID: {p.Id} | Nome: {p.Nome} | Preço: {p.Preco}");
            }
        }

        static void AdicionarAoCarrinho()
        {
            Console.Write("ID do Produto: ");
            int id = int.Parse(Console.ReadLine());

            Produto produto = produtos.Find(p => p.Id == id);

            if (produto == null)
            {
                Console.WriteLine("Produto não encontrado.");
                return;
            }

            Console.Write("Quantidade: ");
            int qtd = int.Parse(Console.ReadLine());

            ItemCarrinho item = new ItemCarrinho();
            item.Produto = produto;
            item.Quantidade = qtd;

            carrinho.Itens.Add(item);

            Console.WriteLine("Produto adicionado ao carrinho!");
        }

        static void VerCarrinho()
        {
            Console.WriteLine("\n--- CARRINHO ---");

            double total = 0;

            foreach (var item in carrinho.Itens)
            {
                double subtotal = item.Produto.Preco * item.Quantidade;

                Console.WriteLine($"{item.Produto.Nome} | Qtd: {item.Quantidade} | Subtotal: {subtotal}");

                total += subtotal;
            }

            Console.WriteLine($"TOTAL: {total}");
        }
    }
}
